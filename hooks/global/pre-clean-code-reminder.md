# Pre Hook: Clean Code Reminder

## What it does

Prints a compact coding standards reminder to stdout immediately before Claude creates a new source file. The agent reads this output and applies the rules to the file it is about to write.

## Hook configuration

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "python3 /Users/vrocha/StudioCodeProjectsPersonal/claude/hooks/scripts/clean_code_reminder.py"
    }
  ]
}
```

**Matcher:** `Write` only — fires on new file creation, not on edits (`Edit`, `MultiEdit`). This avoids redundant reminders on every small change.

## Watched extensions

`.py` `.ts` `.tsx` `.js` `.jsx` `.go` `.java` `.kt` `.swift`

Any other file type (JSON, YAML, Markdown, shell scripts, config) exits silently with no output.

## Output

```
[Clean Code — New File: example.py]
- Functions: <=15 lines (body only, not counting signature/docstring)
- Parameters: <=4 per function (use dataclass/dict for more)
- Nesting: <=3 levels deep (if/for/while/try each count)
- Names: descriptive (no single-letter vars outside loop counters i/j/k/n)
- Single responsibility: one function, one job
- No magic numbers: extract to named constants
```

## Rationale

Static rules belong in `CLAUDE.md` (always loaded, zero per-call overhead). This pre hook adds value because it is:
- **Just-in-time**: fires exactly once at the moment of new file creation, not as background context
- **Dynamic**: aware of file type — suppresses output entirely for non-source files
- **Scoped**: `Write`-only means it never adds noise on small edits

## Script location

`hooks/scripts/clean_code_reminder.py`
