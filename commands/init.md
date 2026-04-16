---
description: "Install DevLead on the current project — creates devlead_docs/ with scaffolding and seeds the canonical source of truth."
---

You are running the `/devlead init` command. Your job is to install DevLead onto the current project. This is a one-shot setup command.

## What to do

Run this shell command to perform the install:

```
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}/src" python -m devlead init
```

On Windows (cmd):
```
set "PYTHONPATH=%CLAUDE_PLUGIN_ROOT%\src" && python -m devlead init
```

Read the output. The install command reports every file it created, skipped, or failed on.

## Report the result plainly

Report what happened to the user in plain language. Examples:

- **Happy path:**
  *"DevLead installed successfully. Created 13 files in `devlead_docs/`. When you're ready, run `/devlead interview` to define the project."*

- **Idempotent re-run:**
  *"DevLead is already installed here. No files were changed."*

- **Partial failure:**
  *"DevLead install hit an error on [file]. Details: [error]. Other files were created successfully — you can fix the error and re-run `/devlead init`."*

## What NOT to do

- Do not start the interview automatically after install. Let the user decide when to run `/devlead interview`.
- Do not modify files outside `devlead_docs/`. Install is scoped to that directory only.
- Do not create tasks, make commits, or change project settings on the user's behalf during install.
- Do not edit existing `devlead_docs/` files — install is idempotent and skips anything that already exists.

## After install

Once install succeeds, the project has:

- `devlead_docs/_project_status.md` — flags section, no formal state machine
- `devlead_docs/_project_hierarchy.md` — empty BO/TBO/TTO tree, ready to populate
- `devlead_docs/_living_project.md` — what the project IS (identity and scope)
- `devlead_docs/_living_standing_instructions.md` — rules that persist across sessions
- `devlead_docs/_living_decisions.md` — canonical append-only decision log
- `devlead_docs/_scratchpad.md` and `devlead_docs/_resume.md` — session memory
- `devlead_docs/_intake_features.md` and `devlead_docs/_intake_bugs.md` — intake queues
- `devlead_docs/_aware_features.md` and `devlead_docs/_aware_design.md` — auto-derived awareness
- `devlead_docs/_audit_log.jsonl` — empty audit stream
- `devlead_docs/_promise_ledger.jsonl` — empty commitment ledger
- `devlead_docs/interview_template.md` — the interview playbook for reference

**Lazy living files (FEATURES-0012).** Only three `_living_*.md` files ship by default (project, standing_instructions, decisions). The rest — goals, metrics, technical, design, glossary, risks — are available on demand via `install_addon()` in code; a `/devlead init --add <slug>` CLI flag is a follow-up. Users who want a fresh install without placeholder busywork get exactly that now.

The user should run `/devlead interview` as the next step to populate these files.
