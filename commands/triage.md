---
description: Walk untriaged _scratchpad.md entries and route each to its canonical home
---

# /devlead triage

Usage: `/devlead triage`

## What this does

Interactive walk through current entries in `devlead_docs/_scratchpad.md`.
For each entry, Claude helps the user decide one of five outcomes:

- **(a) Work** - promote to an `_intake_*.md` file (becomes a FEATURES-NNNN,
  BUGS-NNNN, or similar ID). Command:
  `/devlead promote <needle> --into <intake-file>`.
- **(b) Decision** - the entry is a locked choice. Promote to
  `_living_decisions.md` so we capture it and don't contradict ourselves
  later. Command: `/devlead promote <needle> --to decision`.
- **(c) Fact / doc** - reference fact (glossary, risk, standing instruction,
  project description, technical note, goal description). Promote to the
  matching `_living_*.md` via
  `/devlead promote <needle> --to fact --into _living_<slug>.md`.
- **(d) Leave** - entry stays in the scratchpad for a later decision.
- **(e) Archive** - entry is stale, non-moving, or superseded. Archive
  command ships in v1.1; for now, annotate and leave.

The goal of triage is simple: **capture key decisions so we don't
contradict ourselves later, and route actionable work to intake**.
Everything else has an obvious home.

## How Claude should run this

1. List current entries:
   ```
   PYTHONPATH=src python -m devlead scratchpad
   ```

2. For each entry, summarize in 1-2 sentences and ask the user:
   > Entry `<id>`: <title>
   > What would you like to do? (a) work, (b) decision, (c) fact, (d) leave, (e) archive

3. For (a), (b), or (c): run `/devlead promote` with the appropriate flags.

4. For (d) or (e): no file changes in v1 (archive command ships in v1.1).

## What NOT to do

- Do NOT remove content from the scratchpad unless the destination verifiably
  holds the content. This is the zero-information-loss rule.
- Do NOT put a locked decision into `_intake_*.md`; it belongs in
  `_living_decisions.md`. Mixing them pollutes the backlog.
- Do NOT process more than a handful of entries per run. Triage is short
  and deliberate, not a bulk sweep.
- Do NOT guess `proposed_bo` / `proposed_sprint` / `proposed_weight` without
  real context. Leave them as `(needs ...)` defaults.
