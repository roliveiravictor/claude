#!/usr/bin/env python3
import json
import os
import sys

SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".kt", ".swift"}

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

print(f"""[Clean Code — New File: {os.path.basename(file_path)}]
- Functions: <=15 lines (body only, not counting signature/docstring)
- Parameters: <=4 per function (use dataclass/dict for more)
- Nesting: <=3 levels deep (if/for/while/try each count)
- Names: descriptive (no single-letter vars outside loop counters i/j/k/n)
- Single responsibility: one function, one job
- No magic numbers: extract to named constants""")
