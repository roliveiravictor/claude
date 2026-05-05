---
name: GitHub personal account config
description: SSH key and gh CLI account to use for StudioCodeProjectsPersonal projects
type: reference
originSessionId: cf0c7a49-2079-496c-8d6f-b4eb2ece668d
---
Projects under `~/StudioCodeProjectsPersonal/` use the personal GitHub account `roliveiravictor`.

- **SSH key for git push**: `~/.ssh/roliveiravictor` (no `.pub` extension on the private key)
- **gh CLI account**: `gh` is authenticated as `vrocha_meli` (work) only — cannot use `gh pr create` / `gh pr view` for personal repos; open PRs manually on GitHub or ask user to add `roliveiravictor` via `gh auth login`
- **gitconfig URL rewrite**: already set — `git@github.com-personal:roliveiravictor/` maps to `https://github.com/roliveiravictor/`
- **Work account** (`vrocha_meli`) is the default active `gh` account but should NOT be used for these repos
