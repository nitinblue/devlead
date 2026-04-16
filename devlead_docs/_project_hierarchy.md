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
> TTO checkboxes are ONLY checked by DevLead verification, NEVER by Claude.

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
  verify: <shell command or check that DevLead runs; exit 0 = pass>

RULE: Claude NEVER checks a TTO box. DevLead runs the verify command.
If it passes, DevLead checks the box. This prevents Claude from fudging.
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

- [ ] TTO-001: Create _routing_table.md with R1,R2,R4,R5,R6 (weight: 60) [functional]
  verify: test -f devlead_docs/_routing_table.md && grep -c "^## R" devlead_docs/_routing_table.md | grep -q "[5-9]"
- [ ] TTO-002: Add to scaffold + CLAUDE.md read order (weight: 20) [functional]
  verify: test -f src/devlead/scaffold/_routing_table.md.tmpl && grep -q "routing_table" CLAUDE.md
- [ ] TTO-003: Wire into bootstrap.py SessionStart context (weight: 20) [functional]
  verify: grep -q "routing_table" src/devlead/bootstrap.py

#### TBO-002: Hierarchy with change management (weight: 25)
User can: track BOs with deadlines, detect slips, enforce revision justification

- [ ] TTO-004: Extend _project_hierarchy.md schema with date + change mgmt fields (weight: 50) [functional]
  verify: grep -q "start_date" devlead_docs/_project_hierarchy.md && grep -q "revised_date" devlead_docs/_project_hierarchy.md
- [ ] TTO-005: Create hierarchy.py — parse MD into tree, compute convergence (weight: 50) [functional]
  verify: python -c "from devlead.hierarchy import parse, summary; from pathlib import Path; s=parse(Path('devlead_docs/_project_hierarchy.md')); assert len(s)>0; print('ok')"

#### TBO-003: KPI engine (weight: 25)
User can: see computed metrics from real data, not Claude's opinion

- [ ] TTO-006: Create kpi.py — port v1 KPIs for v2 sources (weight: 60) [functional]
  verify: devlead kpi 2>&1 | grep -c ":" | grep -q "[1-9]"
- [ ] TTO-007: Wire into devlead report HTML with dashboard tabs (weight: 40) [non-functional]
  verify: devlead report && grep -q "KPIs" docs/session-report-*.html

#### TBO-004: Dogfood (weight: 20)
User can: see DevLead governing its own development

- [ ] TTO-008: Populate DevLead's own Sprint/BO/TBO/TTO tree (weight: 100) [functional]
  verify: grep -c "^### BO-" devlead_docs/_project_hierarchy.md | grep -q "[3-9]"

### BO-002: DevLead enforces discipline without human code review (weight: 20)
- **Acceptance:** Non-coder user can trust that Claude followed rules, verified by DevLead report — not by reading Python.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-22
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-005: Proactive routing replaces reactive hooks (weight: 40)
User can: see Claude follow the routing table instead of improvising

- [ ] TTO-009: Routing table with triggers + steps per responsibility (weight: 40) [functional]
  verify: grep -q "Triggers:" devlead_docs/_routing_table.md && grep -q "Steps:" devlead_docs/_routing_table.md
- [ ] TTO-010: Routing table validation — test each R path end-to-end on a real project (weight: 30) [functional]
  verify: devlead init /tmp/rt-test && grep -q "devlead:sot" /tmp/rt-test/devlead_docs/_routing_table.md && rm -rf /tmp/rt-test
- [ ] TTO-011: Add R2 always-active guard to CLAUDE.md so LLM self-enforces even without hooks (weight: 30) [functional]
  verify: grep -q "R2 is always active" devlead_docs/_routing_table.md

#### TBO-006: Session report is the trust layer (weight: 30)
User can: open one HTML file and know the truth

- [ ] TTO-012: report.py with install/hooks/commands/intake/audit/modules/git checks (weight: 30) [functional]
  verify: devlead report && test -f docs/session-report-*.html
- [ ] TTO-013: KPI table + hierarchy convergence in report (weight: 30) [functional]
  verify: grep -q "KPIs" docs/session-report-*.html && grep -q "convergence" docs/session-report-*.html
- [ ] TTO-014: Token usage tracking in report via session history (weight: 20) [functional]
  verify: grep -q "Tokenomics" docs/session-report-*.html && grep -q "tokens" docs/session-report-*.html
- [ ] TTO-015: Stop hook auto-runs devlead report + devlead resume at session end (weight: 20) [functional]
  verify: grep -q "Stop" .claude/settings.json && grep -q "devlead" .claude/settings.json

#### TBO-007: DevLead writes its own state files (weight: 30)
User can: trust that _resume.md comes from data, not Claude's opinion

- [ ] TTO-016: resume.py auto-generates _resume.md from hierarchy + intake + audit + git (weight: 50) [functional]
  verify: devlead resume && grep -q "Auto-generated by DevLead" devlead_docs/_resume.md
- [ ] TTO-017: All devlead_docs state files are DevLead-generated, not Claude-written (weight: 50) [functional]
  verify: grep -q "Auto-generated" devlead_docs/_resume.md && grep -q "devlead:sot" devlead_docs/_routing_table.md

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
  verify: test -f AGENTS.md && grep -q "routing_table" AGENTS.md
- [ ] TTO-019: Generate AGENTS.md (Gemini) and CODEX.md (OpenAI) in addition to CLAUDE.md (weight: 30) [functional]
  verify: test -f AGENTS.md && test -f CODEX.md
- [ ] TTO-020: Document which features are MD-only vs Python-required (weight: 30) [non-functional]
  verify: grep -q "MD-only" README.md || grep -q "MD-only" docs/USER_GUIDE.md

#### TBO-009: Python layer is optional enhancement (weight: 50)
User can: add KPI computation + HTML reports by pip installing devlead

- [ ] TTO-021: pip install devlead works (weight: 30) [functional]
  verify: pip show devlead 2>&1 | grep -q "Version"
- [ ] TTO-022: Clear separation: governance (MD) vs computation (Python) in docs (weight: 30) [non-functional]
  verify: grep -q "governance" README.md && grep -q "computation" README.md
- [ ] TTO-023: devlead init detects LLM tool and generates correct config file (weight: 40) [functional]
  verify: python -c "from devlead.bootstrap import generate_section; assert len(generate_section()) > 100"

### BO-004: Session continuity — no more starting from zero (weight: 15)
- **Acceptance:** New session picks up exactly where the last one left off. User does not re-explain context.
- **start_date:** 2026-04-20
- **end_date:** 2026-04-25
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-010: _resume.md is a complete handoff (weight: 40)
User can: start a session and Claude immediately knows what to do

- [ ] TTO-024: Auto-generated resume with convergence + next TTOs + plan pointer (weight: 40) [functional]
  verify: devlead resume && grep -q "Hierarchy convergence" devlead_docs/_resume.md && grep -q "Next TTOs" devlead_docs/_resume.md
- [ ] TTO-025: Resume includes last session's decisions and open questions (weight: 30) [functional]
  verify: grep -q "decisions" devlead_docs/_resume.md || grep -q "open questions" devlead_docs/_resume.md
- [ ] TTO-026: Resume includes routing table summary so LLM doesn't need to read full file (weight: 30) [functional]
  verify: grep -q "routing" devlead_docs/_resume.md

#### TBO-011: Session history tracks progress across sessions (weight: 30)
User can: see convergence trend over time

- [ ] TTO-027: record_session() called at session end with token count (weight: 40) [functional]
  verify: python -c "from devlead.kpi import record_session; print('importable')"
- [ ] TTO-028: Tokenomics KPI shows cost-per-convergence-point trend (weight: 30) [functional]
  verify: devlead kpi 2>&1 | grep -q "Tokenomics"
- [ ] TTO-029: Going-in-Circles KPI warns on zero-delta sessions (weight: 30) [functional]
  verify: devlead kpi 2>&1 | grep -q "Going in Circles"

#### TBO-012: File discipline enforced by DevLead (weight: 30)
User can: trust no rogue files appear outside framework

- [ ] TTO-030: No-file-without-approval rule in routing table R2 (weight: 50) [functional]
  verify: grep -q "file" devlead_docs/_routing_table.md
- [ ] TTO-031: devlead verify-links checks for files outside framework (weight: 50) [functional]
  verify: devlead verify-links 2>&1 | grep -q "verify-links"

### BO-005: DevLead ships to marketplace (weight: 15)
- **Acceptance:** Non-coder can pip install devlead, run devlead init, and have governance active.
- **start_date:** 2026-04-25
- **end_date:** 2026-04-30
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-013: Packaging (weight: 40)
User can: install DevLead with one command

- [ ] TTO-032: pyproject.toml + pip install -e . works (weight: 50) [functional]
  verify: pip show devlead 2>&1 | grep -q "Version: 0.2"
- [ ] TTO-033: Publish to PyPI (weight: 25) [functional]
  verify: pip install devlead --dry-run 2>&1 | grep -q "devlead"
- [ ] TTO-034: Publish to Claude Code plugin marketplace (weight: 25) [functional]
  verify: test -f .claude-plugin/plugin.json && grep -q "0.2" .claude-plugin/plugin.json

#### TBO-014: Documentation for non-coders (weight: 40)
User can: understand what DevLead does without reading code

- [ ] TTO-035: README.md — one-sentence pitch + install + what it does (weight: 40) [non-functional]
  verify: test -f README.md && wc -l README.md | awk '{exit ($1 > 20 ? 0 : 1)}'
- [ ] TTO-036: User guide: "I installed DevLead, now what?" walkthrough (weight: 40) [non-functional]
  verify: test -f docs/USER_GUIDE.md && wc -l docs/USER_GUIDE.md | awk '{exit ($1 > 30 ? 0 : 1)}'
- [ ] TTO-037: Example session transcript showing DevLead in action (weight: 20) [non-functional]
  verify: test -f docs/example-session.md

#### TBO-015: Quality gate before publish (weight: 20)
User can: trust the published version works

- [ ] TTO-038: Install on fresh project, full user journey passes (weight: 50) [functional]
  verify: mkdir -p /tmp/dlt && devlead init /tmp/dlt && devlead report /tmp/dlt && rm -rf /tmp/dlt
- [ ] TTO-039: Install on one of Nitin's other 9 projects, real session works (weight: 50) [functional]
  verify: echo "requires manual verification by Nitin"

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
  verify: grep -q "pricing\|free\|paid" README.md || grep -q "pricing" docs/USER_GUIDE.md
- [ ] TTO-041: Value proposition page: "Claude says done. Was it?" (weight: 50) [non-functional]
  verify: grep -q "Claude says done" README.md

#### TBO-017: Distribution (weight: 30)
User can: find DevLead where they already look

- [ ] TTO-042: GitHub repo public with README + license (weight: 40) [non-functional]
  verify: test -f LICENSE && test -f README.md
- [ ] TTO-043: Post on relevant communities (weight: 60) [non-functional]
  verify: echo "requires manual verification by Nitin"

#### TBO-018: Validation (weight: 30)
User can: see that real people use DevLead

- [ ] TTO-044: One external user installs and provides feedback (weight: 50) [functional]
  verify: echo "requires manual verification by Nitin"
- [ ] TTO-045: Iterate based on feedback, ship fix within 24 hours (weight: 50) [functional]
  verify: echo "requires manual verification by Nitin"
