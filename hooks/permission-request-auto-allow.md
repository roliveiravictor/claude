# permission-request-auto-allow

**Event:** `PermissionRequest`
**Matcher:** `""` (matches all permission prompts)
**Type:** `command`

Fires on every permission prompt. Emits a JSON `{"behavior": "allow"}` decision only when `tool_name` is in a narrow allowlist of tools that carry zero write or exec risk — eliminating permission-prompt noise for read-only operations without widening the attack surface.

> **Warning (Anthropic):** "Keep the matcher as narrow as possible. Matching on `.*` or leaving the matcher empty would auto-approve every permission prompt, including file writes and shell commands." The `SAFE_TOOLS` set here is intentionally minimal — never add `Bash`, `Write`, `Edit`, or `MultiEdit`.

## Auto-allowed tools

| Tool | Reason |
|------|--------|
| `ExitPlanMode` | Plan → execute transition (Anthropic's own example) |
| `Read` | File reads — no mutations |
| `Glob` | Directory glob — no mutations |
| `LS` | Directory listing — no mutations |

## Script

```python
python3 - <<'PYEOF'
import json, sys

data = json.load(sys.stdin)
tool_name = data.get("tool_name", "")

SAFE_TOOLS = {
    "ExitPlanMode",
    "Read",
    "Glob",
    "LS",
}

if tool_name in SAFE_TOOLS:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"}
        }
    }))

sys.exit(0)
PYEOF
```

## settings.json fragment

```json
"PermissionRequest": [
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
