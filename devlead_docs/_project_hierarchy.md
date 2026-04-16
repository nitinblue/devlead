# Project Hierarchy

<!-- devlead:sot
  purpose: "Sprint / BO / TBO / TTO work tree with change management"
  owner: "user+claude"
  canonical_for: ["work_hierarchy"]
  lineage:
    receives_from: ["_intake_*.md (via promotion)"]
    migrates_to: []
  lifetime: "permanent"
  last_audit: "2026-04-16"
-->

> The BO -> TBO -> TTO tree with weights. Drives all convergence math.
> BO nodes carry change-management fields for deadline tracking.

<!--
Schema reference:

## Sprint <N> — <name>

### BO-<id>: <name> (weight: <0-100>)
- **Acceptance:** <observable / measurable criterion>
- **start_date:** YYYY-MM-DD
- **end_date:** YYYY-MM-DD
- **actual_date:** (pending) | YYYY-MM-DD | (missed YYYY-MM-DD)
- **revised_date:** (none) | YYYY-MM-DD
- **revision_justification:** (none) | <reason for revision>

#### TBO-<id>: <name> (weight: <0-100>)
User can: <user-visible outcome>

- [ ] TTO-<id>: <name> (weight: <0-100>) [functional|non-functional]
- [x] TTO-<id>: <name> (weight: <0-100>) [functional] — DONE

Convergence: computed from [x]/[ ] checkbox state x weights, rolling up TTO -> TBO -> BO.
-->

---

## Sprint 1 — DevLead v2 Launch

### BO-001: DevLead governs via MD-driven routing (weight: 40)
- **Acceptance:** Any LLM reads the routing table and follows predefined paths for all 5 responsibilities. Non-coder user can verify via HTML report.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-20
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-001: Routing table is the brain (weight: 30)
User can: install DevLead and have any LLM self-govern via markdown

- [x] TTO-001: Create _routing_table.md with R1,R2,R4,R5,R6 (weight: 60) [functional]
- [ ] TTO-002: Add to scaffold + CLAUDE.md read order (weight: 20) [functional]
- [ ] TTO-003: Wire into bootstrap.py SessionStart context (weight: 20) [functional]

#### TBO-002: Hierarchy with change management (weight: 25)
User can: track BOs with deadlines, detect slips, enforce revision justification

- [x] TTO-004: Extend _project_hierarchy.md schema with date + change mgmt fields (weight: 50) [functional]
- [ ] TTO-005: Create hierarchy.py — parse MD into tree, compute convergence (weight: 50) [functional]

#### TBO-003: KPI engine (weight: 25)
User can: see computed metrics from real data, not Claude's opinion

- [ ] TTO-006: Create kpi.py — port v1 KPIs for v2 sources (weight: 60) [functional]
- [ ] TTO-007: Wire into devlead report HTML with dashboard tabs (weight: 40) [non-functional]

#### TBO-004: Dogfood (weight: 20)
User can: see DevLead governing its own development

- [x] TTO-008: Populate DevLead's own Sprint/BO/TBO/TTO tree (weight: 100) [functional]

### BO-002: DevLead ships to marketplace (weight: 35)
- **Acceptance:** Non-coder can pip install devlead, run devlead init, and have governance active.
- **start_date:** 2026-04-20
- **end_date:** 2026-04-30
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-005: Packaging (weight: 50)
User can: install DevLead with one command

- [x] TTO-009: pyproject.toml + pip install -e . works (weight: 50) [functional]
- [ ] TTO-010: Publish to PyPI or Claude Code marketplace (weight: 50) [functional]

#### TBO-006: Documentation (weight: 50)
User can: understand what DevLead does without reading code

- [ ] TTO-011: README.md with one-sentence pitch + install instructions (weight: 50) [non-functional]
- [ ] TTO-012: User guide for non-coders (weight: 50) [non-functional]

### BO-003: First revenue (weight: 25)
- **Acceptance:** At least one paying user or $100 MRR by May 8.
- **start_date:** 2026-04-30
- **end_date:** 2026-05-08
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-007: Go-to-market (weight: 100)
User can: find, install, and pay for DevLead

- [ ] TTO-013: Pricing model defined (weight: 30) [non-functional]
- [ ] TTO-014: Landing page or marketplace listing (weight: 40) [non-functional]
- [ ] TTO-015: Test with one real user outside Nitin (weight: 30) [functional]
