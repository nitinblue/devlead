---
description: Set, show, or clear the current focus by flipping intake entry status
---

# /devlead focus

Usage:
  /devlead focus                           # show all in_progress entries
  /devlead focus show                      # same as above
  /devlead focus <intake-id>               # flip <intake-id> status to in_progress
  /devlead focus clear                     # reset all in_progress entries to pending

## What this does

Tracks which intake entry (or entries) Claude is actively working on by
flipping the `status` field in the intake entry body. No separate session
state file - the intake file itself is the canonical source of truth.

Status lifecycle for an intake entry:

| Status | Meaning |
|---|---|
| `pending` | Just created; not yet worked on |
| `in_progress` | Currently being implemented (this is focus) |
| `promoted` | Moved into `_project_hierarchy.md` as a TBO/TTO (Day 4+) |
| `rejected` | Decided not to do |

Multiple entries can be `in_progress` simultaneously (e.g. a feature plus
a related bug). `/devlead focus show` lists every `in_progress` entry
across all `_intake_*.md` files.

## Why status-in-body, not a separate file

Earlier design considered `_session_state.json` as a separate focus tracker.
Rejected because:
- The intake entry already has a `status` lifecycle; adding a parallel
  tracking file creates two sources of truth that can drift.
- Focus is naturally visible when reading the intake file; no extra file
  to open.
- Multiple concurrent in_progress entries work naturally without any
  additional schema.

## How Claude should run this

```
PYTHONPATH=src python -m devlead focus FEATURES-0003
PYTHONPATH=src python -m devlead focus show
PYTHONPATH=src python -m devlead focus clear
```

## When to use

- **At the start of a work session:** set focus to the intake entry you're implementing.
- **When switching tasks mid-session:** set focus on the new entry (the old one stays in_progress unless you clear).
- **When doing non-code work (docs, research, capture):** clear focus so the gate doesn't nag.
- **Before committing:** run `/devlead focus show` to verify the current focus matches the intake ID your commit should reference.

## What NOT to do

- Do NOT hand-edit the `Status` field in an intake file; use this command so
  the update is consistent and can be audit-logged later.
- Do NOT leave stale `in_progress` entries around after a task is done.
  Clear them or promote them.
- Do NOT set focus on an entity that isn't in any `_intake_*.md`. The lookup
  will fail and you'll get an error.
