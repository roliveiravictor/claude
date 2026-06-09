# Post Hook: Clean Code Validator

## What it does

After every file write or edit, analyzes the affected source file for objective code quality violations and prints a structured report. The agent reads this output and refactors violations immediately, closing the enforcement loop without user intervention.

## Hook configuration

```json
{
  "matcher": "Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "python3 /Users/vrocha/StudioCodeProjectsPersonal/claude/hooks/scripts/clean_code_validator.py"
    }
  ]
}
```

## Checks

| Check | Threshold | Method |
|-------|-----------|--------|
| Function length | ≤15 lines (body only, excluding def line and docstring) | Python: AST; Other: brace tracking |
| Parameter count | ≤4 fixed params (`*args`/`**kwargs` excluded) | Python: AST; Other: comma count |
| Nesting depth | ≤3 levels per function (`if`/`for`/`while`/`with`/`try` each count) | Python: AST visitor; Other: brace depth |
| Magic numbers | No bare numeric literals except `0`, `1`, `-1`, `2` | Python: AST only |

## Language support

**Python (`.py`)** — uses stdlib `ast` module for precise analysis. Resets nesting counter per function scope so nested functions are evaluated independently.

**Other languages (`.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.java`, `.kt`, `.swift`)** — regex heuristics. Function/parameter/nesting checks are approximate; magic number check not applied.

## Exceptions

- **Test files** (`test_*.py`, `*_test.py`, `*.test.ts`, `*.spec.ts`): parameter count check is skipped — fixtures legitimately need many params.
- **Non-source files** (JSON, YAML, Markdown, shell, config): hook exits silently.
- **Syntax errors**: prints `parse error: skipping analysis` and exits 0 (never blocks).

## Output formats

Violations found:
```
[Clean Code Violations] src/service.py
  - `process_user_data` (line 42): 23 lines (max 15)
  - `handle_request` (line 71): 6 parameters (max 4)
  - `validate` (line 89): nesting depth 4 (max 3)

Please refactor the above before continuing.
```

All clean:
```
[Clean Code] src/service.py — OK
```

## How agents should respond

On receiving a violations report, refactor the flagged functions in the same file before proceeding to the next task. Do not suppress or ignore the report.

## Script location

`hooks/scripts/clean_code_validator.py`
