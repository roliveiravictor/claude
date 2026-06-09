#!/usr/bin/env python3
import ast
import json
import os
import re
import sys

MAX_FUNCTION_LINES = 15
MAX_PARAMETERS = 4
MAX_NESTING_DEPTH = 3
EXEMPT_NUMBERS = {0, 1, -1, 2}
SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt", ".swift"}


def is_test_file(path: str) -> bool:
    name = os.path.basename(path)
    return name.startswith("test_") or name.endswith("_test.py") or name.endswith(".test.ts") or name.endswith(".spec.ts")


# ── Python AST checks ──────────────────────────────────────────────────────────

def _is_docstring(node: ast.stmt) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def check_function_lengths(tree: ast.Module) -> list[str]:
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        first_stmt = node.body[0]
        start = first_stmt.lineno if not _is_docstring(first_stmt) else (
            node.body[1].lineno if len(node.body) > 1 else node.end_lineno
        )
        body_lines = node.end_lineno - start + 1
        if body_lines > MAX_FUNCTION_LINES:
            violations.append(f"  - `{node.name}` (line {node.lineno}): {body_lines} lines (max {MAX_FUNCTION_LINES})")
    return violations


def check_parameter_counts(tree: ast.Module, skip: bool) -> list[str]:
    if skip:
        return []
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        n_params = len(node.args.args) + len(node.args.posonlyargs)
        if n_params > MAX_PARAMETERS:
            violations.append(f"  - `{node.name}` (line {node.lineno}): {n_params} parameters (max {MAX_PARAMETERS})")
    return violations


class _NestingVisitor(ast.NodeVisitor):
    NESTING_NODES = (
        ast.If, ast.For, ast.While, ast.With, ast.Try,
        ast.ExceptHandler, ast.AsyncFor, ast.AsyncWith,
    )

    def __init__(self):
        self.violations: list[str] = []
        self._depth = 0
        self._func_name = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        saved_name, saved_depth = self._func_name, self._depth
        self._func_name, self._depth = node.name, 0
        self.generic_visit(node)
        self._func_name, self._depth = saved_name, saved_depth

    visit_AsyncFunctionDef = visit_FunctionDef

    def _visit_nesting(self, node):
        self._depth += 1
        if self._depth > MAX_NESTING_DEPTH and self._func_name:
            self.violations.append(
                f"  - `{self._func_name}` (line {node.lineno}): nesting depth {self._depth} (max {MAX_NESTING_DEPTH})"
            )
        self.generic_visit(node)
        self._depth -= 1

    def visit_If(self, node):       self._visit_nesting(node)
    def visit_For(self, node):      self._visit_nesting(node)
    def visit_While(self, node):    self._visit_nesting(node)
    def visit_With(self, node):     self._visit_nesting(node)
    def visit_Try(self, node):      self._visit_nesting(node)
    def visit_ExceptHandler(self, node): self._visit_nesting(node)
    def visit_AsyncFor(self, node): self._visit_nesting(node)
    def visit_AsyncWith(self, node): self._visit_nesting(node)


def check_nesting_depths(tree: ast.Module) -> list[str]:
    visitor = _NestingVisitor()
    visitor.visit(tree)
    seen: set[str] = set()
    unique = []
    for v in visitor.violations:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def _in_annotation_or_default(node: ast.AST, tree: ast.Module) -> bool:
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if field in ("annotation", "returns") and value is node:
                return True
            if field == "defaults" and isinstance(value, list) and node in value:
                return True
            if field == "kw_defaults" and isinstance(value, list) and node in value:
                return True
    return False


def check_magic_numbers(tree: ast.Module) -> list[str]:
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, (int, float)):
            continue
        if node.value in EXEMPT_NUMBERS:
            continue
        violations.append(f"  - magic number `{node.value}` (line {node.lineno}): extract to a named constant")
    return violations


def validate_python(filepath: str) -> list[str]:
    with open(filepath, encoding="utf-8", errors="replace") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filepath)
    except SyntaxError:
        return [f"  - parse error: skipping analysis (file may have syntax errors)"]

    skip_params = is_test_file(filepath)
    violations = []
    violations.extend(check_function_lengths(tree))
    violations.extend(check_parameter_counts(tree, skip=skip_params))
    violations.extend(check_nesting_depths(tree))
    violations.extend(check_magic_numbers(tree))
    return violations


# ── Regex heuristics for non-Python languages ──────────────────────────────────

_FUNC_PATTERN = re.compile(
    r"""
    (?:function\s+\w+\s*\(            # JS/TS: function foo(
    | (?:async\s+)?function\s*\(       # JS: anonymous function
    | \w+\s*[:=]\s*(?:async\s+)?\(.*?\)\s*(?::\s*\w[\w<>, [\]|&?]*?)?\s*=>  # arrow
    | (?:public|private|protected|static|async|override)[\w\s]*\w+\s*\(  # Java/Kotlin
    | func\s+\w+\s*\(                  # Go/Swift
    )
    """,
    re.VERBOSE,
)


def _count_top_level_commas(params: str) -> int:
    depth, count = 0, 0
    for ch in params:
        if ch in "(<[{":
            depth += 1
        elif ch in ")>]}":
            depth -= 1
        elif ch == "," and depth == 0:
            count += 1
    return count


def validate_other(filepath: str) -> list[str]:
    with open(filepath, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    violations = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _FUNC_PATTERN.search(line)
        if not m:
            i += 1
            continue

        func_start_lineno = i + 1
        paren_start = line.find("(", m.start())
        if paren_start == -1:
            i += 1
            continue

        # Extract parameter list
        depth = 0
        param_chars: list[str] = []
        j = paren_start
        full = "".join(lines[i:])
        for ch in full[paren_start:]:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            else:
                if depth == 1:
                    param_chars.append(ch)
        params = "".join(param_chars).strip()
        if params:
            n_params = _count_top_level_commas(params) + 1
            if n_params > MAX_PARAMETERS:
                violations.append(
                    f"  - function (line {func_start_lineno}): {n_params} parameters (max {MAX_PARAMETERS})"
                )

        # Measure body length via brace tracking
        brace_depth = 0
        body_start = None
        body_end = None
        pos = line.find("{", m.start())
        search_lines = lines[i:i + MAX_FUNCTION_LINES + 20]
        for li, sl in enumerate(search_lines):
            start_col = (line.find("{", m.start()) if li == 0 else 0)
            for ci, ch in enumerate(sl):
                if li == 0 and ci < start_col:
                    continue
                if ch == "{":
                    brace_depth += 1
                    if brace_depth == 1:
                        body_start = i + li + 1
                elif ch == "}":
                    brace_depth -= 1
                    if brace_depth == 0 and body_start is not None:
                        body_end = i + li + 1
                        break
            if body_end is not None:
                break

        if body_start is not None and body_end is not None:
            body_lines = body_end - body_start
            if body_lines > MAX_FUNCTION_LINES:
                violations.append(
                    f"  - function (line {func_start_lineno}): {body_lines} lines (max {MAX_FUNCTION_LINES})"
                )

        i += 1

    return violations


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SOURCE_EXTENSIONS:
        sys.exit(0)

    if not os.path.exists(file_path):
        sys.exit(0)

    if ext == ".py":
        violations = validate_python(file_path)
    else:
        violations = validate_other(file_path)

    label = os.path.relpath(file_path) if not os.path.isabs(file_path) else file_path

    if violations:
        print(f"[Clean Code Violations] {label}")
        for v in violations:
            print(v)
        print("\nPlease refactor the above before continuing.")
    else:
        print(f"[Clean Code] {label} — OK")


if __name__ == "__main__":
    main()
