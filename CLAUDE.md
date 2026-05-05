@RTK.md

## RTK full-signal recovery

If an RTK-compressed command output looks truncated or insufficient to diagnose a failure, read the matching raw log under `~/.local/share/rtk/tee/` (newest file) to recover the full unfiltered signal before concluding.

---

## Git Safety Rules — MANDATORY

Before running any of the following git commands, you **MUST** stop and ask the user for explicit confirmation. Describe exactly what the command will do and wait for approval. This applies regardless of context or how urgent the task seems.

### Always confirm before running:

| Operation | Examples |
|-----------|---------|
| Force push | `git push --force`, `git push -f`, `git push origin main --force` |
| Delete remote branch | `git push origin --delete <branch>`, `git push --delete <remote> <branch>` |
| Delete local branch | `git branch -D <branch>`, `git branch -d <branch>` |
| Discard all working changes | `git checkout -- .`, `git restore .`, `git restore --source=HEAD .` |
| Hard reset | `git reset --hard *` |
| Force clean | `git clean -f`, `git clean -fd`, `git clean -fdx` |
| Interactive rebase | `git rebase -i *` |
| Rebase onto | `git rebase --onto *` |
| Delete tag | `git tag -d *`, `git push origin --delete <tag>` |
| Any `--force` or `-f` flag on a git command that modifies remote state |

### Confirmation message format:

Before running, say something like:
> "This will **delete the remote branch `feature/foo`** from `origin`. This cannot be undone easily. Proceed?"

Only proceed after the user explicitly says yes (e.g., "yes", "proceed", "go ahead", "ok").

---

## Plan Mode Routing

Sub-agent pipelines by request type:

```
Bug / incident / failing test:
  debugger (RCA) → user review
    → backend-architect (plan) → user approval
      → implementer → user review
        → test-automator (QA) → user review
          → api-documenter (docs) → user review

Performance / SLO breach / scaling issue:
  performance-engineer (analysis) → user review
    → backend-architect (plan) → user approval
      → implementer → user review
        → test-automator (QA) → user review
          → api-documenter (docs) → user review

Security audit / vulnerability / dependency alert / compliance:
  security-auditor (Security Analysis Report) → user review
    → backend-architect (plan) → user approval
      → implementer → user review
        → test-automator (QA) → user review
          → api-documenter (docs) → user review

Plan marked PENDING SECURITY REVIEW (new trust boundary, auth/crypto change):
  security-auditor (Security Analysis Report) → user review
    → backend-architect (revised plan) → user approval
      → implementer → user review
        → test-automator (QA) → user review
          → api-documenter (docs) → user review

New feature / change (no known bug, perf issue, or security concern):
  backend-architect (plan) → user approval
    → implementer → user review
      → test-automator (QA) → user review
        → api-documenter (docs) → user review

Documentation only (no code change):
  api-documenter (docs) → user review
```

**Implementer** is language-routed (see Implementation Routing below).
All plans and handbacks are passed verbatim — never summarized.

### Trigger: debugger

Invoke `debugger` when the request is:
- A bug report, incident, or unexpected production behaviour
- A failing test the user cannot explain

Pass it the full error output, stack trace, or failing test output.
After `debugger` hands back, present the RCA to the user and wait for
explicit instruction before proceeding to `backend-architect`.
If `debugger` stops early (3 failed repros), surface its partial report
and ask the user how to proceed.

Skip `debugger` and go straight to `backend-architect` when:
- The root cause is already known and stated by the user
- The request is a new feature with no bug component

### Trigger: performance-engineer

Invoke `performance-engineer` when the request is:
- An SLO breach, latency spike, or throughput regression
- A capacity or scaling question
- A load-testing or profiling request
- A performance regression (even when the cause seems obvious — measure first)

Pass it the full complaint plus any attached metrics, traces, or dashboards.
Ask the user for target SLOs (p50/p95/p99 latency, throughput, resource
budget) before invoking — if unavailable, the agent will document
[ASSUMED SLO] and proceed.
After `performance-engineer` hands back, present the Performance Analysis
Report to the user and wait for explicit instruction before proceeding to
`backend-architect`.
If the agent stops early (3 failed measurements), surface its partial
report and ask the user how to proceed.

Skip `performance-engineer` and go straight to `backend-architect` when:
- The bottleneck is already quantified and the user just wants the fix designed
- The request is a new feature with no performance concern stated

### Trigger: security-auditor

Invoke `security-auditor` when the request is:
- A security audit, penetration test scope, or threat model review
- A vulnerability report or CVE affecting a dependency
- A compliance or supply-chain check
- A change that backend-architect has marked "PENDING SECURITY REVIEW"
  (new trust boundary, auth model change, crypto change, new third-party
  data flow)

Before invoking, collect from the user: audit scope (full repo, diff,
specific path) and threat model context (auth model, trust boundaries,
data sensitivity). If unavailable, the agent will document
[ASSUMED SCOPE] / [ASSUMED TRUST MODEL] and proceed.

Pass the audit request plus any dependency alerts, incident details, or
the backend-architect plan marked PENDING SECURITY REVIEW — verbatim.
After `security-auditor` hands back, present the Security Analysis Report
to the user and wait for explicit instruction before proceeding.

- If the report contains High/Critical findings, do not proceed to
  `backend-architect` without user confirmation on how to handle them.
- If findings require architectural remediation, pass the Security
  Analysis Report to `backend-architect` as a constraint document.
- If any finding is marked "RE-AUDIT REQUIRED", invoke
  `security-auditor` again after the fix lands before considering
  the pipeline complete.

Skip `security-auditor` and go straight to `backend-architect` when:
- The security posture of the change is already fully documented in
  an existing docs/security/ report and no new trust boundaries are
  introduced
- The request is a trivial internal change with no trust boundary contact

### Planning Phase

In Plan Mode, always delegate to `backend-architect`. Do not produce
plans directly.

- Pass the user's requirement plus any upstream analysis reports
  (debugger RCA, performance-engineer Performance Analysis Report,
  security-auditor Security Analysis Report) and relevant context
  (file paths, constraints, prior decisions).
- Return the Development Plan verbatim for user review.
- Exit Plan Mode only after the user approves the plan.
- Treat the approved plan's Specification as authoritative during
  implementation; Implementation Plan as guidance.

### Implementation Routing (post-plan approval)

| Project language | Implementation agent |
|-----------------|---------------------|
| Python (any framework) | `python-pro` |
| Other / mixed | Implement directly |

**Detecting a Python project**: check for `pyproject.toml`, `setup.py`,
`setup.cfg`, `requirements*.txt`, or a majority of `.py` files in the
affected area. When in doubt, ask.

**Task sizing — preventing stream-idle-timeout**: A single `python-pro`
call that touches more than 4 files or contains more than 3 distinct
logical changes (new feature, edit existing module, write tests) risks
an idle stream-close mid-run. Before invoking, count the affected files
listed in the Development Plan's Implementation Plan section:

- **≤ 4 files, 1–2 logical changes** — single call, pass the full
  Development Plan verbatim.
- **5–8 files or 3 logical changes** — split into 2 sequential calls.
  Call 1 covers production code changes. Call 2 covers tests and any
  remaining files. Pass the Development Plan plus a handoff note stating
  what Call 1 completed.
- **9+ files or 4+ logical changes** — split into 3 sequential calls:
  Call 1: core domain / orchestration changes.
  Call 2: adapters, aggregators, and supporting modules.
  Call 3: tests and fixture files.
  Each call receives the Development Plan plus a running handoff summary
  of what prior calls completed and what files were written.

Wait for each call to hand back cleanly before starting the next. If a
call times out mid-run, resume by passing the same Development Plan with
a handoff note listing the files already written (recoverable from the
partial handback output).

Pass the full approved Development Plan verbatim. After all calls
complete, present the consolidated handback (Summary, Changes,
Verification, Plan deviations, Adjacent issues) and wait for user review
before proceeding.

### QA Routing (post-implementation)

Invoke `test-automator` after a clean implementation handback:

- Pass both the approved Development Plan and the implementation
  handback verbatim.
- If the handback shows failing tests or unresolved deviations, surface
  the issue to the user first — do not invoke `test-automator`.
- After handback, present it in full and wait for further instructions.

### Documentation Routing (post-QA)

Invoke `api-documenter` after `test-automator` hands back cleanly, or
directly for documentation-only requests:

- **Post-implementation**: pass the approved Development Plan, the
  implementer handback, and the merged diff verbatim. If a
  security-auditor or performance-engineer report exists for this
  change, pass its path — api-documenter will link, not summarize.
- **PR descriptions**: pass the Development Plan, diff, and commit
  messages. Optionally include handback reports for the Linked reports
  section.
- **Documentation-only requests** (no code change): invoke directly
  with the relevant source files and any existing plan.

After `api-documenter` hands back, present it in full (Summary, Files
written, Drift detected, Unverified sections, Linked reports, Adjacent
doc gaps) and wait for further instructions.

Skip `api-documenter` when:
- The user explicitly opts out ("no docs needed", "skip documenter")
- The change is internal-only with no public API or README surface
- The change is a pure test or configuration update with no
  behavioral effect on documented interfaces

### Exceptions (skip sub-agents, handle directly)

- Trivial single-file changes with no architectural impact
- User explicitly requests a quick answer or asks to bypass planning
- Pure questions about existing code with no change proposed
- User explicitly skips a stage ("skip tests", "no RCA needed", etc.)
