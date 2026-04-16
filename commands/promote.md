---
description: Promote a scratchpad entry to an intake file, a decision log, or a living file
---

# /devlead promote

Usage:
  /devlead promote <needle> --into <_intake_*.md> [--forced]
  /devlead promote <needle> --to decision [--forced]
  /devlead promote <needle> --to fact --into <_living_*.md> [--forced]

## What this does

Scratchpad entries come in three shapes. Promotion routes each to its
canonical home:

- **Work** (features, bugs, tasks) -> an `_intake_*.md` file. The new intake
  entry records `source: scratchpad:<entry-id>`. The scratchpad entry gets a
  `> **Promoted:**` cross-reference line.
- **Decision** (locked choices) -> `_living_decisions.md` (append-only
  canonical decisions archive). The scratchpad entry gets a `> **Migrated:**`
  cross-reference line.
- **Fact / doc** (glossary terms, project descriptions, technical notes,
  risks, standing instructions, goals) -> any `_living_*.md` file. Same
  cross-reference shape as decisions.

`<needle>` is a substring matched against scratchpad entry IDs and titles.
First match in file order wins.

`--forced` marks the resulting entry with `origin: forced` for KPI tracking
when the promotion was user-dictated outside the normal triage flow.

## How Claude should run this

### Promote to work (intake)
```
PYTHONPATH=src python -m devlead promote memory-cohesion --into _intake_features.md
```

### Promote to decision
```
PYTHONPATH=src python -m devlead promote sprint-rename --to decision
```

### Promote to fact
```
PYTHONPATH=src python -m devlead promote tto-definition --to fact --into _living_glossary.md
```

### Forced (user dictated outside normal flow)
```
PYTHONPATH=src python -m devlead promote critical-typo --into _intake_bugs.md --forced
```

## Distinction from /devlead ingest

- **`/devlead ingest <plan> --into <file>`** is for EXTERNAL plugin output
  (e.g. superpowers plans, specs from other plugins). Claude points it at a
  plan file on disk.
- **`/devlead promote <needle> [options]`** is for INTERNAL scratchpad
  entries. It reads the scratchpad directly and routes.

Both can end up in the same intake file. Promote is the scratchpad-first
path; ingest is the plugin-first path.

## What NOT to do

- Do NOT promote a scratchpad entry without first verifying its content is
  suitable for its destination (work vs decision vs fact).
- Do NOT promote one entry to multiple destinations. Pick one canonical home.
- Do NOT promote an entry whose body is empty or placeholder text. Refine
  it in the scratchpad first.
