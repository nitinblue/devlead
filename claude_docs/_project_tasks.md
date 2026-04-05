# Project Tasks

> Type: PROJECT
> Last updated: 2026-04-05 | Open: 0 | In Progress: 0 | Done: 12

Note: Original 12 implementation tasks all DONE. New work tracked via FEAT intake items.

## Active

| ID | Task | Story | Priority | Status | Assignee | Blockers |
|----|------|-------|----------|--------|----------|----------|
| TASK-000 | Project skeleton — pyproject.toml, src layout, CLI stub | E-001 | P1 | DONE | claude | — |
| TASK-001 | hooks.py — hook_allow, hook_block, hook_context | E-001 | P1 | DONE | claude | — |
| TASK-002 | state_machine.py — 7 states, transitions, gates, checklists | E-001 | P1 | DONE | claude | TASK-001 ✅ |
| TASK-003 | config.py — devlead.toml parsing, defaults | E-001 | P1 | DONE | claude | — |
| TASK-004 | doc_parser.py — markdown table parsing, builtin variables | E-002 | P1 | DONE | claude | — |
| TASK-005 | kpi_engine.py — 30 built-in KPIs, formula evaluator, plugins | E-002 | P1 | DONE | claude | TASK-003 ✅, TASK-004 ✅ |
| TASK-006 | Wire KPIs into CLI — devlead status, devlead kpis | E-002 | P1 | DONE | claude | TASK-005 ✅ |
| TASK-007 | scaffold/ + devlead init — templates, hook merge, gitignore | E-003 | P1 | DONE | claude | TASK-002 ✅ |
| TASK-008 | rollover.py — monthly archival, open item carry-forward | E-003 | P1 | DONE | claude | TASK-004 ✅ |
| TASK-009 | doctor + session history — health check, LLM Learning Curve | E-003 | P2 | DONE | claude | TASK-005 ✅ |
| TASK-010 | portfolio.py — multi-project workspace, cross-project KPIs | E-004 | P2 | DONE | claude | TASK-005 ✅ |
| TASK-011 | collab.py — cross-project channel, inbox scanning, final polish | E-004 | P2 | DONE | claude | TASK-010 ✅ |
