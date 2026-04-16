# Project Stories

> Type: PROJECT
> Last updated: 2026-04-05

## What This File Is

Maps every Story to its Epic and TBO with PM fields.
Stories are technical deliverables -- they are enablers, not business progress by themselves.
A story only contributes to progress when its parent TBO is completed.

## Story Tracker

| ID | Story | Epic | TBO Link | Status | DoD | Risks | Dependencies |
|----|-------|------|----------|--------|-----|-------|--------------|
| S-001 | Project skeleton with pip-installable CLI | E-001 | TBO-1, TBO-3 | DONE | `pip install -e .` works, `devlead --help` prints usage | None | None |
| S-002 | Hook output helpers -- exit 0/2 protocol | E-001 | TBO-1 | DONE | `hooks.py` returns allow/block JSON, tests pass | None | S-001 |
| S-003 | State machine -- 7 states, transitions, gates | E-001 | TBO-1 | DONE | All 7 states reachable, gate blocks invalid transitions | State explosion if states grow | S-001 |
| S-004 | TOML configuration with defaults | E-001 | TBO-1 | DONE | `devlead.toml` parsed, defaults applied for missing keys | None | S-001 |
| S-005 | Markdown doc parser -- tables, status, builtins | E-002 | TBO-1 | DONE | Parses any devlead_docs table by header name | Malformed markdown edge cases | S-001 |
| S-006 | Safe formula evaluator -- no eval() | E-002 | TBO-1 | DONE | Recursive descent parser handles +,-,*,/,if,min,max | Complex formulas may be slow | S-005 |
| S-007 | 30 built-in KPIs across 3 categories | E-002 | TBO-1 | DONE | All 30 KPIs compute from doc_parser output | KPI definitions may change | S-005, S-006 |
| S-008 | Custom TOML KPIs and Python plugin KPIs | E-002 | TBO-1 | DONE | User-defined KPIs in devlead.toml load and evaluate | Plugin security (no eval) | S-006, S-007 |
| S-009 | KPI dashboard terminal output | E-002 | TBO-1 | DONE | `devlead kpis` and `devlead dashboard` render cleanly | Terminal width issues | S-007 |
| S-010 | devlead init -- scaffold, hook merge, gitignore | E-003 | TBO-1 | DONE | `devlead init` creates devlead_docs/, hooks, .gitignore | Existing file conflicts | S-001 |
| S-011 | Monthly rollover with configurable policy | E-003 | TBO-1 | DONE | Date and size triggers work, archives created | Data loss if rollover fails mid-write | S-004, S-005 |
| S-012 | devlead doctor (healthcheck) | E-003 | TBO-1 | DONE | `devlead healthcheck` reports missing files, stale docs | False positives | S-004 |
| S-013 | Session history + LLM Learning Curve KPI | E-003 | TBO-1 | DONE | session_history.jsonl written, delta computed | JSONL growth unbounded | S-005, S-007 |
| S-014 | Portfolio workspace -- register, list, remove | E-004 | TBO-2 | DONE | `devlead portfolio register/list/remove` works | Path conflicts across OS | S-004 |
| S-015 | Cross-project KPIs -- 7 portfolio metrics | E-004 | TBO-2 | DONE | Portfolio KPIs aggregate across registered projects | Stale project data | S-007, S-014 |
| S-016 | Collab channel -- .collab/ inbox/outbox, sync | E-004 | TBO-2 | DONE | 4 message types sent and received, sync works | Message ordering, conflicts | S-014 |
| S-017 | Token and effort tracking per task | E-002 | TBO-1 | DONE | Hook captures token count from stdin, session timestamps tied to active task, aggregated to story level | Transcript format may change across Claude versions | S-005, S-013 |

| S-018 | PyPI and GitHub distribution | E-003 | TBO-3 | IN_PROGRESS | Package uploaded to PyPI, GitHub repo public, pip install devlead works | PyPI name conflict, credentials | S-001 |
## Summary

- Stories total: 17
- Done: 17
- Open: 1
- All stories are linked to at least one TBO (no shadow work).