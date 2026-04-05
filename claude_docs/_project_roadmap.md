# Project Roadmap

> Type: PROJECT
> Last updated: 2026-04-05

## Epics

| ID | Epic | Priority | Status |
|----|------|----------|--------|
| E-001 | Core Engine — state machine + hooks + config | P1 | IN_PROGRESS |
| E-002 | KPI Engine — 30 built-in + custom + plugins | P1 | OPEN |
| E-003 | Developer Experience — init, rollover, doctor | P1 | OPEN |
| E-004 | Multi-Project — portfolio + collab channel | P2 | OPEN |

## Stories

- [x] S-001: Project skeleton with pip-installable CLI (E-001)
- [ ] S-002: Hook output helpers — exit code 0/2 protocol (E-001)
- [ ] S-003: State machine — 7 states, transitions, gate enforcement (E-001)
- [ ] S-004: TOML configuration with defaults (E-001)
- [ ] S-005: Markdown doc parser — tables, status counting, builtin vars (E-002)
- [ ] S-006: Safe formula evaluator — no eval(), recursive descent (E-002)
- [ ] S-007: 30 built-in KPIs across 3 categories (E-002)
- [ ] S-008: Custom TOML KPIs and Python plugin KPIs (E-002)
- [ ] S-009: KPI dashboard terminal output (E-002)
- [ ] S-010: devlead init — scaffold, hook merge, gitignore (E-003)
- [ ] S-011: Monthly rollover with configurable policy (E-003)
- [ ] S-012: devlead doctor — health check (E-003)
- [ ] S-013: Session history + LLM Learning Curve KPI (E-003)
- [ ] S-014: Portfolio workspace — register, list, remove projects (E-004)
- [ ] S-015: Cross-project KPIs — 7 portfolio-level metrics (E-004)
- [ ] S-016: Collab channel — .collab/ inbox/outbox, sync (E-004)

## Business Objectives

| Objective | Metric | Target |
|-----------|--------|--------|
| OBJ-1: Working single-project governance | `devlead init` + full state lifecycle works | Epics 1-3 |
| OBJ-2: Working multi-project governance | `devlead portfolio` + collab works | Epic 4 |
| OBJ-3: Distributable product | `pip install devlead` from PyPI works | After all epics |
| OBJ-4: First paying customer | $49 Pro tier purchase | After OBJ-3 |
