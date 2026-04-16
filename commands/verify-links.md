---
description: Walk cross-references in devlead_docs/ and report broken refs + orphans
---

# /devlead verify-links

Usage:
  /devlead verify-links                    # scan devlead_docs/ in current directory

## What this does

Walks every cross-reference in `devlead_docs/` and reports two classes of
problems:

1. **Broken refs** - a reference points to something that does not exist:
   - Intake `source` fields referencing a missing scratchpad entry or file.
   - Scratchpad `> **Promoted:**` lines citing an intake ID not found in any
     `_intake_*.md`.
   - SOT `receives_from` / `migrates_to` referencing a `.md` file that does
     not exist in `devlead_docs/`.

2. **Orphans** (advisory) - intake entries with `status: pending` that are
   older than 7 days. These are not errors, just nudges to triage or close
   stale items.

Every run writes one audit event to `_audit_log.jsonl`:
- `verify_pass` when no broken refs or orphans are found.
- `verify_broken` with counts when problems exist.
