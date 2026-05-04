# precompact-transcript-backup

**Event:** `PreCompact`
**Matchers:** `auto`, `manual`
**Type:** `command` (async — does not block compaction)

Fires before context compaction (both auto-triggered and manual `/compact`). Copies the current transcript to `~/.claude/transcript-backups/` with a timestamp prefix, preserving the full conversation before it is summarized.

Backups:
- Auto-compaction: `~/.claude/transcript-backups/<YYYYMMDDTHHmmSS>-transcript.jsonl`
- Manual compaction: `~/.claude/transcript-backups/<YYYYMMDDTHHmmSS>-manual-transcript.jsonl`

Guards against [anthropics/claude-code#13668](https://github.com/anthropics/claude-code/issues/13668) — `CLAUDE_TRANSCRIPT_PATH` may be empty on some macOS versions; the script exits 0 gracefully in that case.

## Script (auto)

```bash
bash -c '
  SRC="${CLAUDE_TRANSCRIPT_PATH:-}"
  if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
    echo "PreCompact: no transcript path, skipping" >&2
    exit 0
  fi
  BACKUP_DIR="${HOME}/.claude/transcript-backups"
  mkdir -p "$BACKUP_DIR"
  cp "$SRC" "${BACKUP_DIR}/$(date +%Y%m%dT%H%M%S)-transcript.jsonl"
  exit 0
'
```

## Script (manual)

```bash
bash -c '
  SRC="${CLAUDE_TRANSCRIPT_PATH:-}"
  if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then exit 0; fi
  BACKUP_DIR="${HOME}/.claude/transcript-backups"
  mkdir -p "$BACKUP_DIR"
  cp "$SRC" "${BACKUP_DIR}/$(date +%Y%m%dT%H%M%S)-manual-transcript.jsonl"
  exit 0
'
```

## settings.json fragment

```json
"PreCompact": [
  {
    "matcher": "auto",
    "hooks": [
      { "type": "command", "async": true, "command": "bash -c '\n  SRC=..." }
    ]
  },
  {
    "matcher": "manual",
    "hooks": [
      { "type": "command", "async": true, "command": "bash -c '\n  SRC=..." }
    ]
  }
]
```
