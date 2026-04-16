# Bug Intake

> Type: INTAKE
> Last updated: 2026-04-05 | Open: 8 | Closed: 0

## Active

| Key | Item | Source | Added | Status | Priority | Notes |
|-----|------|--------|-------|--------|----------|-------|
| BUG-001 | Intake process not enforced -- AI finds issues but doesn't register in intake files | audit | 2026-04-05 | OPEN | P1 | Root cause: no gate check that intake was updated. AI proposed work plan on stale snapshot. |
| BUG-002 | Status file says FEAT-014 registered but intake has FEAT-016 -- status not updated when intake grows | audit | 2026-04-05 | OPEN | P1 | _project_status.md drifted from _intake_features.md. No cross-validation. |
| BUG-003 | Session summary reported from model memory, not from md files | audit | 2026-04-05 | OPEN | P1 | Model generated freeform "Done" list instead of referencing TASK-*, FEAT-*, GAP-*, BUG-* keys from devlead_docs/. Breaks system-of-record principle. Session reports must be derived from the files, not conversation context. |
| BUG-004 | Subagents bypass Edit/Write gate by using sed/bash instead | testing | 2026-04-05 | OPEN | P2 | Gate blocks Edit/Write tools (exit code 2 works), but subagents fell back to `sed -i` via Bash tool. Adding Bash matcher blocks ALL bash commands (including devlead CLI, pytest, etc.) making the system unusable. Bash gate removed. Known limitation -- Bash bypass requires smarter approach (parse command for file-write patterns). Downgraded to P2. |
| BUG-005 | ORIENT checklist not enforced -- session proceeded without reading required files | testing | 2026-04-05 | OPEN | P2 | Transition gate DOES block if checklist incomplete (tested and confirmed). But the Edit/Write gate only checks state, not checklist. Model can edit files in EXECUTE without completing ORIENT first if it transitions there. Downgraded to P2 -- the transition gate is the primary enforcement. |
| BUG-006 | session_history.jsonl missing -- file not created on session start | testing | 2026-04-05 | OPEN | P2 | devlead start creates session_state.json but session_history.jsonl doesn't exist. Either it should be created on start or the rename from claude_docs broke the path. |
| BUG-007 | effort and doctor commands not wired into CLI | testing | 2026-04-05 | OPEN | P2 | effort.py and doctor.py modules exist in src/devlead/ but cli.py doesn't dispatch to them. `devlead effort` and `devlead doctor` return "Unknown command". |
| BUG-008 | Intake file header counts stale -- gap command detects mismatch | testing | 2026-04-05 | OPEN | P2 | _intake_bugs.md says open=3 but has 6 rows. _intake_features.md says open=38 but has 48. _intake_gaps.md says open=9 but has 14. Headers not auto-updated when items are added. |

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|
