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

## Sprint 1 — DevLead v2 Core Product

### BO-001: MD-driven routing governs all DevLead responsibilities (weight: 25)
- **Acceptance:** Any LLM reads the routing table and follows predefined paths for all 5 responsibilities. Non-coder user can verify via HTML report.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-20
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-001: Routing table is the brain (weight: 30)
User can: install DevLead and have any LLM self-govern via markdown

- [x] TTO-001: Create _routing_table.md with R1,R2,R4,R5,R6 (weight: 60) [functional]
- [x] TTO-002: Add to scaffold + CLAUDE.md read order (weight: 20) [functional]
- [x] TTO-003: Wire into bootstrap.py SessionStart context (weight: 20) [functional]

#### TBO-002: Hierarchy with change management (weight: 25)
User can: track BOs with deadlines, detect slips, enforce revision justification

- [x] TTO-004: Extend _project_hierarchy.md schema with date + change mgmt fields (weight: 50) [functional]
- [x] TTO-005: Create hierarchy.py — parse MD into tree, compute convergence (weight: 50) [functional]

#### TBO-003: KPI engine (weight: 25)
User can: see computed metrics from real data, not Claude's opinion

- [x] TTO-006: Create kpi.py — port v1 KPIs for v2 sources (weight: 60) [functional]
- [x] TTO-007: Wire into devlead report HTML with dashboard tabs (weight: 40) [non-functional]

#### TBO-004: Dogfood (weight: 20)
User can: see DevLead governing its own development

- [x] TTO-008: Populate DevLead's own Sprint/BO/TBO/TTO tree (weight: 100) [functional]

### BO-002: DevLead enforces discipline without human code review (weight: 20)
- **Acceptance:** Non-coder user can trust that Claude followed rules, verified by DevLead report — not by reading Python.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-22
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-005: Proactive routing replaces reactive hooks (weight: 40)
User can: see Claude follow the routing table instead of improvising

- [x] TTO-009: Routing table with triggers + steps per responsibility (weight: 40) [functional]
- [ ] TTO-010: Routing table validation — test each R path end-to-end on a real project (weight: 30) [functional]
- [ ] TTO-011: Add R2 always-active guard to CLAUDE.md so LLM self-enforces even without hooks (weight: 30) [functional]

#### TBO-006: Session report is the trust layer (weight: 30)
User can: open one HTML file and know the truth

- [x] TTO-012: report.py with install/hooks/commands/intake/audit/modules/git checks (weight: 30) [functional]
- [x] TTO-013: KPI table + hierarchy convergence in report (weight: 30) [functional]
- [ ] TTO-014: Token usage tracking in report via session history (weight: 20) [functional]
- [ ] TTO-015: Stop hook auto-runs devlead report + devlead resume at session end (weight: 20) [functional]

#### TBO-007: DevLead writes its own state files (weight: 30)
User can: trust that _resume.md comes from data, not Claude's opinion

- [x] TTO-016: resume.py auto-generates _resume.md from hierarchy + intake + audit + git (weight: 50) [functional]
- [ ] TTO-017: All devlead_docs state files are DevLead-generated, not Claude-written (weight: 50) [functional]

### BO-003: DevLead works with any LLM, not just Claude (weight: 15)
- **Acceptance:** Install DevLead on a project, use it with Gemini CLI or Cursor, routing table still governs.
- **start_date:** 2026-04-22
- **end_date:** 2026-04-28
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-008: MD-driven core has zero Python dependency for governance (weight: 50)
User can: get value from DevLead without pip install

- [ ] TTO-018: Routing table works standalone — test with Gemini CLI reading AGENTS.md (weight: 40) [functional]
- [ ] TTO-019: Generate AGENTS.md (Gemini) and CODEX.md (OpenAI) in addition to CLAUDE.md (weight: 30) [functional]
- [ ] TTO-020: Document which features are MD-only vs Python-required (weight: 30) [non-functional]

#### TBO-009: Python layer is optional enhancement (weight: 50)
User can: add KPI computation + HTML reports by pip installing devlead

- [x] TTO-021: pip install devlead works (weight: 30) [functional]
- [ ] TTO-022: Clear separation: governance (MD) vs computation (Python) in docs (weight: 30) [non-functional]
- [ ] TTO-023: devlead init detects LLM tool and generates correct config file (weight: 40) [functional]

### BO-004: Session continuity — no more starting from zero (weight: 15)
- **Acceptance:** New session picks up exactly where the last one left off. User does not re-explain context.
- **start_date:** 2026-04-20
- **end_date:** 2026-04-25
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-010: _resume.md is a complete handoff (weight: 40)
User can: start a session and Claude immediately knows what to do

- [x] TTO-024: Auto-generated resume with convergence + next TTOs + plan pointer (weight: 40) [functional]
- [ ] TTO-025: Resume includes last session's decisions and open questions (weight: 30) [functional]
- [ ] TTO-026: Resume includes routing table summary so LLM doesn't need to read full file (weight: 30) [functional]

#### TBO-011: Session history tracks progress across sessions (weight: 30)
User can: see convergence trend over time

- [ ] TTO-027: record_session() called at session end with token count (weight: 40) [functional]
- [ ] TTO-028: Tokenomics KPI shows cost-per-convergence-point trend (weight: 30) [functional]
- [ ] TTO-029: Going-in-Circles KPI warns on zero-delta sessions (weight: 30) [functional]

#### TBO-012: File discipline enforced by DevLead (weight: 30)
User can: trust no rogue files appear outside framework

- [ ] TTO-030: No-file-without-approval rule in routing table R2 (weight: 50) [functional]
- [ ] TTO-031: devlead verify-links checks for files outside framework (weight: 50) [functional]

### BO-005: DevLead ships to marketplace (weight: 15)
- **Acceptance:** Non-coder can pip install devlead, run devlead init, and have governance active.
- **start_date:** 2026-04-25
- **end_date:** 2026-04-30
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-013: Packaging (weight: 40)
User can: install DevLead with one command

- [x] TTO-032: pyproject.toml + pip install -e . works (weight: 50) [functional]
- [ ] TTO-033: Publish to PyPI (weight: 25) [functional]
- [ ] TTO-034: Publish to Claude Code plugin marketplace (weight: 25) [functional]

#### TBO-014: Documentation for non-coders (weight: 40)
User can: understand what DevLead does without reading code

- [ ] TTO-035: README.md — one-sentence pitch + install + what it does (weight: 40) [non-functional]
- [ ] TTO-036: User guide: "I installed DevLead, now what?" walkthrough (weight: 40) [non-functional]
- [ ] TTO-037: Example session transcript showing DevLead in action (weight: 20) [non-functional]

#### TBO-015: Quality gate before publish (weight: 20)
User can: trust the published version works

- [ ] TTO-038: Install on fresh project, full user journey passes (weight: 50) [functional]
- [ ] TTO-039: Install on one of Nitin's other 9 projects, real session works (weight: 50) [functional]

### BO-006: First revenue (weight: 10)
- **Acceptance:** At least one paying user or $100 MRR by May 8.
- **start_date:** 2026-04-30
- **end_date:** 2026-05-08
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-016: Pricing and positioning (weight: 40)
User can: understand what they pay for and why

- [ ] TTO-040: Pricing model: free MD core + paid Python enhancement tier (weight: 50) [non-functional]
- [ ] TTO-041: Value proposition page: "Claude says done. Was it?" (weight: 50) [non-functional]

#### TBO-017: Distribution (weight: 30)
User can: find DevLead where they already look

- [ ] TTO-042: GitHub repo public with README + license (weight: 40) [non-functional]
- [ ] TTO-043: Post on relevant communities (Claude Discord, AI dev forums) (weight: 60) [non-functional]

#### TBO-018: Validation (weight: 30)
User can: see that real people use DevLead

- [ ] TTO-044: One external user installs and provides feedback (weight: 50) [functional]
- [ ] TTO-045: Iterate based on feedback, ship fix within 24 hours (weight: 50) [functional]
