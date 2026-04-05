# Feature Intake

> Type: INTAKE
> Last updated: 2026-04-05 | Open: 5 | Closed: 0

## Active

| Key | Item | Source | Added | Status | Priority | Notes |
|-----|------|--------|-------|--------|----------|-------|
| FEAT-001 | Token usage KPIs — cost per task, wasted tokens, efficiency | user | 2026-04-05 | OPEN | P3 | V2 — needs Claude transcript_path from hook input |
| FEAT-002 | Claude Workflow hooks — governance for scheduled agents | user | 2026-04-05 | OPEN | P3 | V2 — pre/post workflow gates, DoD for scheduled tasks |
| FEAT-003 | Rollover policy — by date OR by file size (lines threshold) | user | 2026-04-05 | OPEN | P2 | Config: rollover_trigger = "date" or "size", max_lines = 500 |
| FEAT-004 | Cross-project guard — user-level hook protects all DevLead projects | user | 2026-04-05 | OPEN | P1 | `devlead install-guard` sets up ~/.claude/settings.json hook. Prevents ungoverned edits from other sessions. |
| FEAT-005 | File path enforcement in gate — inspect stdin JSON for target path | user | 2026-04-05 | OPEN | P1 | Gate checks WHERE files are written, not just IF. Blocks memory writes outside UPDATE, enforces naming convention. |

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|
