# auto-format-on-edit

**Event:** `PostToolUse`
**Matcher:** `Edit|Write|MultiEdit`
**Type:** `command`
**Scope:** Project — formatter is stack-dependent; this file uses `ruff` for Python

Fires after every `Write`, `Edit`, or `MultiEdit`. Reads `tool_input.file_path` from stdin via `jq` and runs the formatter on the changed file only — not the entire project. Output is silenced (`2>/dev/null || true`) so a formatter failure never blocks Claude.

> **Context cost note:** Each formatted file triggers a system reminder that consumes context. On long sessions, consider moving formatting into the `Stop` hook so it runs once per turn rather than per file edit.

## Formatter variants

| Stack | Command |
|-------|---------|
| Python (ruff) | `ruff format "{}"` |
| Python (black) | `python3 -m black --quiet "{}"` |
| JS/TS/JSON/CSS | `npx prettier --write "{}"` |
| Go | `gofmt -w "{}"` |
| Rust | `rustfmt "{}"` |
| Ruby | `rubocop --autocorrect-all --format quiet "{}"` |

## Script (Python / ruff)

```sh
jq -r '.tool_input.file_path // empty' | xargs -I{} ruff format "{}" 2>/dev/null || true
```

## settings.json fragment

```json
"PostToolUse": [
  {
    "matcher": "Edit|Write|MultiEdit",
    "hooks": [
      {
        "type": "command",
        "command": "jq -r '.tool_input.file_path // empty' | xargs -I{} ruff format \"{}\" 2>/dev/null || true"
      }
    ]
  }
]
```
