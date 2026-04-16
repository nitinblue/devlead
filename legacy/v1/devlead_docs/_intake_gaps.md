# Gap Intake

> Type: INTAKE
> Last updated: 2026-04-05 | Open: 14 | Closed: 0

## Active

| Key | Item | Source | Added | Status | Priority | Notes |
|-----|------|--------|-------|--------|----------|-------|
| GAP-001 | Missing LICENSE file -- pyproject.toml says MIT but no LICENSE file exists | audit | 2026-04-05 | OPEN | P1 | Legal compliance. Required for PyPI and GitHub. |
| GAP-002 | Empty README.md -- only contains `# devlead` | audit | 2026-04-05 | OPEN | P1 | Storefront for PyPI and GitHub. Must have install, usage, examples. |
| GAP-003 | Incomplete pyproject.toml -- no authors, urls, classifiers, keywords | audit | 2026-04-05 | OPEN | P1 | PyPI metadata. Package looks abandoned without this. |
| GAP-004 | No MANIFEST.in -- scaffold/ templates may not get packaged | audit | 2026-04-05 | OPEN | P1 | Verify package_data or add MANIFEST.in for scaffold files. |
| GAP-005 | Missing _living_business_objectives.md -- referenced in standing instruction #14 | audit | 2026-04-05 | OPEN | P1 | TBO tracking has no home. Can't compute convergence. |
| GAP-006 | Missing _living_distribution.md -- referenced in standing instruction #17 | audit | 2026-04-05 | OPEN | P1 | Distribution/productionization milestones not tracked. |
| GAP-007 | Missing _project_stories.md -- referenced in status as "added" but doesn't exist | audit | 2026-04-05 | OPEN | P1 | No PM fields (Risks, Delays, Blockers, Dependencies). No TBO linkage. |
| GAP-008 | Roadmap stories S-002 through S-016 unchecked despite tasks being DONE | audit | 2026-04-05 | OPEN | P2 | Roadmap doesn't reflect actual progress. Misleading. |
| GAP-009 | 6 files exceed 200-line rule -- dashboard.py (1323), kpi_engine.py (601), state_machine.py (342), cli.py (331), doc_parser.py (275), portfolio.py (212) | audit | 2026-04-05 | OPEN | P2 | Only dashboard.py tracked as FEAT-015. Others untracked. |
| GAP-010 | Superpowers has zero awareness of DevLead -- no integration between plugins | brainstorm | 2026-04-05 | OPEN | P1 | Superpowers brainstorming/planning skills don't read devlead_docs/, don't check active tasks, don't reference stories or TBOs. They operate independently. DevLead should feed Superpowers, not the other way around. |
| GAP-011 | migrate command doesn't create or append to CLAUDE.md | brainstorm | 2026-04-05 | OPEN | P1 | init merges hooks into .claude/settings.json but neither init nor migrate touch CLAUDE.md. User must manually create CLAUDE.md with DevLead instructions. Plugin onboarding requires this to be automated. |
| GAP-012 | migrate command doesn't install hooks -- only init does | brainstorm | 2026-04-05 | OPEN | P1 | migrate scans for .claude/settings.json but doesn't merge hooks. Existing projects that run migrate get devlead_docs/ but no hook enforcement. |
| GAP-013 | No scaffold template for CLAUDE.md exists | brainstorm | 2026-04-05 | OPEN | P1 | src/devlead/scaffold/ has 11 templates but no CLAUDE.md template. Plugin needs a template that gets appended to project's CLAUDE.md with @import references to devlead_docs/. |
| GAP-014 | Audit log doesn't capture migration actions | brainstorm | 2026-04-05 | OPEN | P2 | Migration creates/skips files but doesn't write any entries to _audit_log.jsonl. No traceability of what happened during onboarding. |

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|

