# Project Tasks

> Type: PROJECT
> Last updated: 2026-04-08 | Open: 10 | In Progress: 0 | Done: 69

Note: Original 12 implementation tasks all DONE. Session 3 governance tasks below.

## Active

| ID | Task | Story | Priority | Status | Assignee | Blockers |
|----|------|-------|----------|--------|----------|----------|
| TASK-000 | Project skeleton -- pyproject.toml, src layout, CLI stub | S-001 | P1 | DONE | claude | -- |
| TASK-001 | hooks.py -- hook_allow, hook_block, hook_context | S-002 | P1 | DONE | claude | -- |
| TASK-002 | state_machine.py -- 7 states, transitions, gates, checklists | S-003 | P1 | DONE | claude | TASK-001 ✅ |
| TASK-003 | config.py -- devlead.toml parsing, defaults | S-004 | P1 | DONE | claude | -- |
| TASK-004 | doc_parser.py -- markdown table parsing, builtin variables | S-005 | P1 | DONE | claude | -- |
| TASK-005 | kpi_engine.py -- 30 built-in KPIs, formula evaluator, plugins | S-007 | P1 | DONE | claude | TASK-003 ✅, TASK-004 ✅ |
| TASK-006 | Wire KPIs into CLI -- devlead status, devlead kpis | S-009 | P1 | DONE | claude | TASK-005 ✅ |
| TASK-007 | scaffold/ + devlead init -- templates, hook merge, gitignore | S-010 | P1 | DONE | claude | TASK-002 ✅ |
| TASK-008 | rollover.py -- monthly archival, open item carry-forward | S-011 | P1 | DONE | claude | TASK-004 ✅ |
| TASK-009 | doctor + session history -- health check, LLM Learning Curve | S-012 | P2 | DONE | claude | TASK-005 ✅ |
| TASK-010 | portfolio.py -- multi-project workspace, cross-project KPIs | S-014 | P2 | DONE | claude | TASK-005 ✅ |
| TASK-011 | collab.py -- cross-project channel, inbox scanning, final polish | S-016 | P2 | DONE | claude | TASK-010 ✅ |
| TASK-012 | Governance enforcement -- no-work-without-task gate | S-003 | P1 | DONE | claude | -- |
| TASK-013 | Memory-from-docs-only enforcement | S-003 | P1 | DONE | claude | -- |
| TASK-014 | Scratchpad capture mechanism | S-001 | P1 | DONE | claude | TASK-012 |
| TASK-015 | LICENSE file -- create MIT license | S-001 | P1 | DONE | claude | -- |
| TASK-016 | README.md -- proper project description, install, usage | S-001 | P1 | DONE | claude | -- |
| TASK-017 | pyproject.toml -- authors, urls, classifiers, keywords | S-001 | P1 | DONE | claude | -- |
| TASK-018 | MANIFEST.in / package_data -- ensure scaffold files packaged | S-001 | P1 | DONE | claude | -- |
| TASK-019 | Create _living_business_objectives.md | S-001 | P1 | DONE | claude | -- |
| TASK-020 | Create _living_distribution.md | S-001 | P1 | DONE | claude | -- |
| TASK-021 | Create _project_stories.md with TBO linkage | S-001 | P1 | DONE | claude | -- |
| TASK-022 | Mark TASK-012, TASK-013 DONE, close session 3 work | S-001 | P1 | DONE | claude | -- |
| TASK-023 | Fix roadmap -- check completed stories | S-001 | P2 | DONE | claude | -- |
| TASK-024 | devlead gap command -- automated governance gap detection | S-001 | P1 | DONE | claude | -- |
| TASK-025 | Polish scratchpad + triage CLI | S-001 | P1 | DONE | claude | -- |
| TASK-026 | TBO hierarchy view -- devlead view command showing TBO→Story→Task lineage | S-001 | P1 | DONE | claude | -- |
| TASK-027 | Smart analysis -- devlead analyze command for open-ended project questions | S-001 | P1 | DONE | claude | TASK-026 |
| TASK-028 | Update stale distribution doc -- compliance milestones are done | S-001 | P1 | DONE | claude | -- |
| TASK-029 | Tests for view and analyze commands | S-001 | P1 | DONE | claude | TASK-026, TASK-027 |
| TASK-030 | Interactive triage -- devlead triage command for scratchpad items | S-001 | P1 | DONE | claude | -- |
| TASK-031 | Migration bootstrap -- devlead migrate for existing projects | S-001 | P1 | DONE | claude | -- |
| TASK-032 | Workbook data model -- shared TBO→Story→Task structure | S-001 | P1 | DONE | claude | -- |
| TASK-033 | Rewrite view.py to use workbook model with Option B format | S-001 | P1 | DONE | claude | TASK-032 |
| TASK-034 | Auto-regenerate HTML on transitions and report commands | S-001 | P1 | DONE | claude | TASK-032 |
| TASK-035 | Formalize TBO list with planned/actual dates | S-001 | P1 | DONE | claude | -- |
| TASK-036 | Fix Business tab -- remove raw dump, show only TBOs with timeline | S-001 | P1 | DONE | claude | -- |
| TASK-037 | Rewrite Roadmap tab as workbook view -- TBO→Story→Task with PM attributes | S-001 | P1 | DONE | claude | -- |
| TASK-038 | Business tab Gantt chart -- visual timeline of TBO planned vs actual dates | S-001 | P1 | DONE | claude | -- |
| TASK-039 | Add Gantt chart legend for color coding | S-001 | P1 | DONE | claude | -- |
| TASK-040 | devlead serve -- local HTTP server for interactive dashboard edits | S-001 | P1 | ON_HOLD | claude | -- |
| TASK-041 | Update state machine -- add TRIAGE and PRIORITIZE states | S-003 | P1 | DONE | claude | -- |
| TASK-042 | Fix Gantt timeline -- show planned/actual dates on bars | S-001 | P1 | DONE | claude | -- |
| TASK-043 | Replace Intake tab with Backlog tab -- show FEAT/BUG/GAP by priority after Roadmap | S-001 | P1 | DONE | claude | -- |
| TASK-044 | Dashboard typography -- consistent font sizes, use color not size for hierarchy | S-001 | P1 | DONE | claude | -- |
| TASK-045 | Parse hook stdin for token count and model name | S-017 | P1 | DONE | claude | -- |
| TASK-046 | Track session time per active task in session_state.json | S-017 | P1 | DONE | claude | -- |
| TASK-047 | Aggregate effort to story level in workbook model | S-017 | P1 | DONE | claude | TASK-045, TASK-046 |
| TASK-048 | Tests for token and effort tracking | S-017 | P1 | DONE | claude | TASK-045 |
| TASK-049 | Fix dashboard -- Requirement Type label, header duplicate, tab flipping | S-001 | P1 | DONE | claude | -- |
| TASK-050 | Dashboard fixes -- rename Distribution to Productionize, fix S-017 linkage | S-001 | P1 | DONE | claude | -- |
| TASK-051 | Audit tab -- filter out .py files, show only governance actions | S-001 | P1 | DONE | claude | -- |
| TASK-052 | Fix audit test after .py filter change | S-017 | P1 | DONE | claude | -- |
| TASK-053 | Add token/effort columns to Roadmap tab table | S-017 | P1 | DONE | claude | -- |
| TASK-054 | Package build and PyPI readiness test | S-001 | P1 | DONE | claude | -- |
| TASK-055 | Roadmap tab -- collapsible stories with details/summary HTML | S-001 | P1 | DONE | claude | -- |
| TASK-056 | Roadmap tab -- show full form Tangible Business Outcome on TBO cards | S-001 | P1 | DONE | claude | -- |
| TASK-057 | Roadmap TBO card -- status after description, TBO ID regular bold | S-001 | P1 | DONE | claude | -- |
| TASK-058 | Demo -- show token and duration tracking on a real task | S-017 | P1 | DONE | claude | -- |
| TASK-059 | Create PyPI account at pypi.org and generate API token | S-018 | P1 | OPEN | nitin | -- |
| TASK-060 | Create TestPyPI account at test.pypi.org and generate API token | S-018 | P1 | OPEN | nitin | -- |
| TASK-061 | Upload to TestPyPI -- twine upload --repository testpypi dist/* | S-018 | P1 | OPEN | nitin | TASK-060 |
| TASK-062 | Verify TestPyPI install -- pip install --index-url https://test.pypi.org/simple/ devlead | S-018 | P1 | OPEN | nitin | TASK-061 |
| TASK-063 | Upload to PyPI production -- twine upload dist/* | S-018 | P1 | OPEN | nitin | TASK-059, TASK-062 |
| TASK-064 | Verify PyPI install -- pip install devlead (from fresh venv) | S-018 | P1 | OPEN | nitin | TASK-063 |
| TASK-065 | Create GitHub repo at github.com, push code, make public | S-018 | P1 | OPEN | nitin | -- |
| TASK-066 | Update pyproject.toml URLs with real GitHub repo URL | S-018 | P1 | OPEN | nitin | TASK-065 |
| TASK-067 | Create user setup guide -- getting started with DevLead | S-018 | P1 | DONE | claude | -- |
| TASK-068 | Fix BUG-004/005/006/007/008 -- gate bypass, checklist, session history, CLI wiring, header counts | S-003 | P1 | DONE | claude | -- |
| TASK-069 | Fix GAP-011/012/013 -- migrate should setup CLAUDE.md and hooks | S-001 | P1 | DONE | claude | TASK-068 |
| TASK-070 | Fix GAP-014 -- audit log captures migration actions | S-001 | P2 | DONE | claude | TASK-069 |
| TASK-071 | Refresh intake headers and verify all fixes | S-003 | P1 | DONE | claude | -- |
| TASK-072 | Remove overbroad Bash gate and update scaffold | S-003 | P1 | DONE | claude | -- |
| TASK-073 | Update setup guide with all fixes and install instructions | S-018 | P1 | DONE | claude | -- |
| TASK-074 | Business Convergence Engine -- design spec and gate framework | S-003 | P1 | DONE | claude | -- |
| TASK-075 | Convergence Engine -- data model (BO, weighted TBO/Story), parser, formula | S-003 | P1 | DONE | claude | TASK-074 |
| TASK-076 | Convergence Engine -- 6 KPI instruments | S-003 | P1 | DONE | claude | TASK-075 |
| TASK-077 | Convergence Engine -- dashboard, CLI status, migration | S-003 | P1 | DONE | claude | TASK-075 |
| TASK-078 | Convergence Engine -- CLAUDE.md scaffold for model ownership behavior | S-003 | P1 | DONE | claude | TASK-075 |