---
description: List current intake file entries
---

# /devlead intake

Usage:
  /devlead intake                          # list all _intake_*.md files
  /devlead intake <path-to-intake-file>    # list one file
  /devlead intake <docs-dir>               # list all intake files in docs-dir

## What this does

Lists the entries in DevLead intake files. Intake files are any file matching
`_intake_*.md` in `devlead_docs/` - DevLead recognizes them by prefix, not a
fixed list. Default install ships `_intake_features.md` and `_intake_bugs.md`,
but you can create `_intake_security.md`, `_intake_roadmap_ideas.md`, or any
other `_intake_<slug>.md` you need.

Each entry is printed as `ID  STATUS  TITLE`, grouped per file.

## How Claude should run this

From the project root:

```
PYTHONPATH=src python -m devlead intake
```

For a specific file:

```
PYTHONPATH=src python -m devlead intake devlead_docs/_intake_features.md
```

Output is grouped per file; empty files show `(no entries)`.

## What NOT to do

- Do NOT modify intake files from this command. Use `/devlead ingest` for
  writes and `/devlead triage` for promotion walks.
