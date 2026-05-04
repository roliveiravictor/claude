# stop-test-enforcement

**Event:** `Stop`
**Matcher:** `""` (fires on every stop)
**Type:** `command`
**Scope:** Project — test command is project-specific; this file uses `pytest -q`

Fires when Claude is about to hand back control. Runs the test suite; if it is red, returns `{"decision": "block"}` with up to 2500 chars of failure output so Claude self-corrects before stopping. The `CLAUDE_STOP_HOOK_ACTIVE` environment guard prevents infinite loops.

Exit semantics: `exit 0` + JSON output → Claude reads the decision. `exit 2` → surfaces raw output to the user.

## Test runner variants

| Stack | Command |
|-------|---------|
| Node / Jest / Vitest | `["npm", "test", "--", "--reporter=dot"]` |
| Python (pytest) | `["pytest", "-q"]` |
| Python (verbose failures) | `["pytest", "-q", "--tb=short"]` |
| Go | `["go", "test", "./..."]` |
| Rust | `["cargo", "test", "--quiet"]` |
| Ruby | `["bundle", "exec", "rspec", "--format", "progress"]` |
| Java / Kotlin | `["./gradlew", "test", "--quiet"]` |

## Script

```python
python3 - <<'PYEOF'
import json, os, subprocess, sys

if os.environ.get("CLAUDE_STOP_HOOK_ACTIVE"):
    sys.exit(0)

TEST_CMD = ["pytest", "-q"]

result = subprocess.run(TEST_CMD, capture_output=True, text=True)

if result.returncode == 0:
    sys.exit(0)

output = {
    "decision": "block",
    "reason": (
        "Tests are failing — do not stop until they pass.\n\n"
        + result.stdout[-2000:]
        + result.stderr[-500:]
    )
}
print(json.dumps(output))
sys.exit(0)
PYEOF
```

## settings.json fragment

```json
"Stop": [
  {
    "matcher": "",
    "hooks": [
      {
        "type": "command",
        "command": "python3 - <<'PYEOF'\n..."
      }
    ]
  }
]
```
