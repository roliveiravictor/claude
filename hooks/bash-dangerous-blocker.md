# bash-dangerous-blocker

**Event:** `PreToolUse`
**Matcher:** `Bash`
**Type:** `command` (blocking — exit 2 surfaces stderr to Claude)

Fires before every `Bash` tool call, before the permission system. A Python 3 inline script checks the command string against a static regex denylist. On a match it exits with code 2, which surfaces the stderr message to Claude so it self-corrects. Cannot be bypassed even with `--dangerously-skip-permissions`.

## Blocked patterns

| Pattern | Reason |
|---------|--------|
| `rm -rf`, `rm -r` | Recursive file removal |
| `sudo rm` | Privileged removal |
| `chmod 777` | World-writable permissions |
| `> /etc/` | Overwrite system config |
| `> /dev/sd` | Write to block device |
| `dd if=` | Potential disk wipe |
| `git push --force` | Force-push without lease |
| `git reset --hard` | Discard uncommitted work |
| `:(){ ... };` | Fork bomb |
| `curl \| bash`, `wget \| sh` | Pipe-to-shell install |

## Script

```python
python3 - <<'PYEOF'
import json, sys, re

data = json.load(sys.stdin)
command = data.get("tool_input", {}).get("command", "")

BLOCKED = [
    (r"rm\s+-[rRf]*f[rR]?\s",            "Recursive force-remove is blocked. Use 'git stash' or move files manually."),
    (r"rm\s+-[rR]\s",                     "Recursive remove is blocked. Confirm intent and run manually if needed."),
    (r"sudo\s+rm",                        "sudo rm is blocked unconditionally."),
    (r"chmod\s+777",                      "chmod 777 is blocked. Use the minimum required permissions."),
    (r">\s*/etc/",                        "Overwriting /etc/ files is blocked."),
    (r">\s*/dev/sd",                      "Writing to block devices is blocked."),
    (r"dd\s+if=",                         "dd with if= is blocked — potential disk wipe."),
    (r"git\s+push\s+.*--force(?:\s|$)",   "Force-push is blocked. Use --force-with-lease and confirm branch."),
    (r"git\s+reset\s+--hard",             "Hard reset is blocked. Use 'git stash' first."),
    (r":\(\)\{.*\};",                     "Fork bomb pattern detected and blocked."),
    (r"curl\s+.*\|\s*(bash|sh|zsh|fish)", "Pipe-to-shell installs are blocked. Download and inspect first."),
    (r"wget\s+.*\|\s*(bash|sh|zsh|fish)", "Pipe-to-shell installs are blocked. Download and inspect first."),
]

for pattern, message in BLOCKED:
    if re.search(pattern, command, re.IGNORECASE):
        print(f"BLOCKED: {message}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
PYEOF
```

## settings.json fragment

```json
"PreToolUse": [
  {
    "matcher": "Bash",
    "hooks": [
      {
        "type": "command",
        "command": "python3 - <<'PYEOF'\n..."
      }
    ]
  }
]
```
