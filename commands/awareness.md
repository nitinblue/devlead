---
description: Refresh DevLead self-awareness files (_aware_*.md)
---

# /devlead awareness

Usage: `/devlead awareness`

## What this does

Scans the current project's code (`commands/*.md` and `src/devlead/*.py`) and
regenerates the self-awareness files:

- `devlead_docs/_aware_features.md` - inventory of every slash command, its
  description, command file, and handler location
- `devlead_docs/_aware_design.md` - snapshot of every Python module, its
  purpose (from docstring), public API, line count, and internal dependencies

These files are **derived from code** - they describe the CURRENT state of the
project, not aspirational design. Hand-edits are overwritten on the next run.
The awareness files are read at session start (after `_resume.md` and
`_scratchpad.md`) as primary LLM memory substrate - reducing reliance on
`CLAUDE.md` alone for project context.

## How Claude should run this

From the project root:

```
PYTHONPATH=src python -m devlead awareness
```

Output lists the two files that were refreshed. After running, Claude should
read both `_aware_*.md` files to ground itself in the project's current state.

## When to refresh

- After any significant code change (new module, new command, refactor)
- Before starting a session on an unfamiliar area
- When `CLAUDE.md` or `_resume.md` §14 references behavior that no longer matches the code

v1.1 will auto-refresh on a Stop hook, so manual calls become rare.

## What NOT to do

- Do NOT hand-edit `_aware_*.md` files. They are machine-generated and
  overwritten on every refresh.
- Do NOT use the awareness files as the source of design *intent* - that's
  what `_living_design.md` is for. The awareness files are descriptive, not
  prescriptive.
