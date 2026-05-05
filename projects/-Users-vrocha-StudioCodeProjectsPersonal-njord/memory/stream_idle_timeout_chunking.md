---
name: python-pro task sizing to prevent stream-idle-timeout
description: Split large python-pro calls into 2-3 sequential focused calls to avoid stream-idle-close errors. Thresholds defined in Implementation Routing section of CLAUDE.md.
type: feedback
---
Anthropic's streaming infrastructure closes idle connections after extended
inactivity between tool calls. A single python-pro call covering 5+ files
will often exceed this threshold when the model spends time reasoning
between sequential reads and edits.

**Rule**: Before invoking python-pro, count affected files from the
Development Plan's Implementation Plan section:

| File count | Logical changes | Action |
|------------|----------------|--------|
| ≤ 4        | 1–2            | Single call — pass full plan verbatim |
| 5–8        | 3              | 2 calls: [1] prod code, [2] tests + remaining files |
| 9+         | 4+             | 3 calls: [1] domain/orchestration, [2] adapters/aggregators, [3] tests |

**Handoff protocol**: Each subsequent call receives the Development Plan
plus a handoff note listing which files were written in prior calls.

**Recovery**: If a call times out, resume with the same plan and a
handoff note listing files already written (check partial handback output).

**Why:** Focused calls complete in 10–15 min per chunk vs 30+ min
monolithic runs, staying well within idle-close windows.
