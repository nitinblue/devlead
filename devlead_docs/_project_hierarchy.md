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

> TTO checkboxes are ONLY checked by DevLead verification, NEVER by Claude.
> Functional TTOs have verify: commands. Non-functional can be marked by Claude.
> Self-correction KPI: K_INCONSISTENCY tracks how often hierarchy drifts from foundations page.

---

## Sprint 1 — DevLead Works For Real

### BO-001: Claude cannot cheat (weight: 30)
- **Acceptance:** Claude physically cannot write code without a tracked work item. Every edit is traced. Every session ends with proof. The user doesn't need to read Python to verify.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-25
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-001: Hard block on untracked work (weight: 25)
User can: trust that every line of code traces to an intake entry

- [ ] TTO-001: PreToolUse gate exits 2 when no intake entry is in_progress (weight: 30) [functional]
  verify: devlead focus clear && echo '{"tool_name":"Edit","tool_input":{"file_path":"src/app.py"}}' | devlead gate PreToolUse 2>&1; test $? -eq 2
- [ ] TTO-002: Gate logs every check (pass/block) to _audit_log.jsonl (weight: 20) [functional]
  verify: wc -l devlead_docs/_audit_log.jsonl | awk '{exit ($1 > 5 ? 0 : 1)}'
- [ ] TTO-003: Exempt paths configurable via devlead.toml (weight: 15) [functional]
  verify: grep -q "exempt_paths" src/devlead/config.py
- [ ] TTO-004: K_BYPASS KPI tracks discipline violation rate (weight: 20) [functional]
  verify: devlead kpi 2>&1 | grep -q "K_BYPASS"
- [ ] TTO-005: Enforcement mode configurable — hard/soft/warning (weight: 15) [functional]
  verify: grep -q "hard\|soft\|warning" src/devlead/config.py

#### TBO-002: Every session ends with proof (weight: 25)
User can: open one HTML file and see what actually happened

- [ ] TTO-006: Stop hook auto-runs dashboard + resume + record_session at session end (weight: 35) [functional]
  verify: grep -q "Stop" .claude/settings.json
- [ ] TTO-007: Dashboard has 10 tabs with real data (weight: 25) [functional]
  verify: devlead dashboard && test -f docs/dashboard-*.html
- [ ] TTO-008: Definition of Done tab runs verify: commands and shows pass/fail (weight: 25) [functional]
  verify: grep -q "Def of Done" docs/dashboard-*.html
- [ ] TTO-009: Session history records tokens + convergence per session (weight: 15) [functional]
  verify: python -c "from devlead.kpi import record_session; from pathlib import Path; record_session(Path('devlead_docs'), 1000)"

#### TBO-003: The LLM's instructions are always truthful (weight: 25)
User can: trust that CLAUDE.md reflects the actual project state

- [ ] TTO-010: CLAUDE.md 100% derived from devlead_docs/ — zero hardcoded strings (weight: 30) [functional]
  verify: grep -q "auto-generated from devlead_docs" CLAUDE.md
- [ ] TTO-011: devlead init regenerates CLAUDE.md from current file state (weight: 20) [functional]
  verify: devlead init . 2>&1 | grep -q "derived from devlead_docs"
- [ ] TTO-012: Routing table embedded in CLAUDE.md, not referenced as separate file (weight: 25) [functional]
  verify: grep -q "## R1" CLAUDE.md && grep -q "## R2" CLAUDE.md
- [ ] TTO-013: Current convergence + focus shown in CLAUDE.md (weight: 25) [functional]
  verify: grep -q "convergence" CLAUDE.md

#### TBO-004: Documents stay in sync automatically (weight: 25)
User can: change one file and all related files update — no manual commands

- [ ] TTO-014: SOT blocks define receives_from/migrates_to on every file (weight: 15) [functional]
  verify: grep -c "devlead:sot" devlead_docs/*.md | grep -v ":0$" | wc -l | awk '{exit ($1 > 10 ? 0 : 1)}'
- [ ] TTO-015: DAG propagation engine reads SOT relationships and triggers downstream updates (weight: 30) [functional]
  verify: echo "not yet built"
- [ ] TTO-016: Changing _routing_table.md auto-regenerates CLAUDE.md (weight: 20) [functional]
  verify: echo "not yet built"
- [ ] TTO-017: Changing _project_hierarchy.md auto-regenerates _resume.md (weight: 20) [functional]
  verify: echo "not yet built"
- [ ] TTO-018: K_DRIFT KPI tracks how often files are out of sync (weight: 15) [functional]
  verify: echo "not yet built"

### BO-002: I always know where my project stands (weight: 25)
- **Acceptance:** At any moment, the user can see: what % is done, what's overdue, what's next, how many tokens were spent, and whether Claude followed the rules. All computed from data, never from Claude's opinion.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-28
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-005: Work pipeline from idea to done (weight: 30)
User can: go from "I have an idea" to tracked, decomposed, prioritized work

- [ ] TTO-019: Scratchpad captures raw input verbatim (weight: 10) [functional]
  verify: python -c "from devlead.scratchpad import append_entry; from pathlib import Path; append_entry(Path('/tmp/t.md'),'test','body')" && rm /tmp/t.md
- [ ] TTO-020: Triage routes to 3 targets — work, decision, fact (weight: 10) [functional]
  verify: grep -q "decision" src/devlead/cli.py && grep -q "fact" src/devlead/cli.py
- [ ] TTO-021: Intake ingest with bidirectional trace (scratchpad <-> intake) (weight: 15) [functional]
  verify: python -c "from devlead.bridge import ingest_from_scratchpad; print('ok')"
- [ ] TTO-022: Intake to hierarchy promotion command (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-023: BO/TBO/TTO hierarchy with weights summing to 100 per parent (weight: 20) [functional]
  verify: python -c "from devlead.hierarchy import parse; from pathlib import Path; s=parse(Path('devlead_docs/_project_hierarchy.md')); assert len(s)>0"
- [ ] TTO-024: Convergence computed from verified checkbox state, not Claude marking (weight: 20) [functional]
  verify: devlead kpi 2>&1 | grep -q "Sprint convergence"

#### TBO-006: Deadlines enforced with change management (weight: 20)
User can: set deadlines on BOs and be alerted when they slip — no silent failures

- [ ] TTO-025: BOs have start_date, end_date, actual_date, revised_date, justification (weight: 30) [functional]
  verify: grep -q "start_date" devlead_docs/_project_hierarchy.md && grep -q "revised_date" devlead_docs/_project_hierarchy.md
- [ ] TTO-026: Dashboard timeline tab shows Gantt bars with overdue highlighting (weight: 30) [functional]
  verify: grep -q "gantt" docs/dashboard-*.html || grep -q "Timelines" docs/dashboard-*.html
- [ ] TTO-027: Missed deadline triggers mandatory change management (justification required) (weight: 40) [functional]
  verify: grep -q "revision_justification" devlead_docs/_routing_table.md

#### TBO-007: 25 KPIs from real data (weight: 20)
User can: see metrics that are computed, never guessed

- [ ] TTO-028: KPI engine reads from audit log + hierarchy + intake (weight: 25) [functional]
  verify: devlead kpi 2>&1 | grep -c ":" | awk '{exit ($1 >= 15 ? 0 : 1)}'
- [ ] TTO-029: Token tracking per TTO (mandatory) (weight: 25) [functional]
  verify: python -c "from devlead.effort import record_effort; from pathlib import Path; record_effort(Path('devlead_docs'),'TTO-001',500)"
- [ ] TTO-030: Tokenomics KPI — cost per convergence point (weight: 25) [functional]
  verify: devlead kpi 2>&1 | grep -q "Tokenomics"
- [ ] TTO-031: K_INCONSISTENCY KPI — tracks self-correction events (weight: 25) [functional]
  verify: echo "not yet built"

#### TBO-008: Intent routing makes Claude follow the plan (weight: 30)
User can: say anything and DevLead routes it to the right process — or stays out of the way

- [ ] TTO-032: Routing table defines 5+ responsibilities with triggers + steps (weight: 15) [functional]
  verify: grep -c "^## R" devlead_docs/_routing_table.md | awk '{exit ($1 >= 5 ? 0 : 1)}'
- [ ] TTO-033: UserPromptSubmit hook classifies intent and injects matched route (weight: 30) [functional]
  verify: echo "not yet built"
- [ ] TTO-034: Adding new responsibility = add markdown section, zero code (weight: 15) [functional]
  verify: grep -q "To add a new responsibility" devlead_docs/_routing_table.md
- [ ] TTO-035: Routing tested in fresh session — Claude follows R2 without being told (weight: 25) [functional]
  verify: echo "requires fresh session test by Nitin"
- [ ] TTO-036: Routing tested — Claude follows R1 when asked to add a feature (weight: 15) [functional]
  verify: echo "requires fresh session test by Nitin"

### BO-003: Sessions never start from zero (weight: 20)
- **Acceptance:** Close the CLI, open it tomorrow. Claude immediately knows: what was done, what's next, what's blocked, and what the rules are. The user says nothing — DevLead tells Claude everything.
- **start_date:** 2026-04-20
- **end_date:** 2026-04-28
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-009: _resume.md is a complete handoff (weight: 40)
User can: start a session and Claude immediately knows what to do

- [ ] TTO-037: Resume auto-generated from hierarchy + intake + audit + git (weight: 25) [functional]
  verify: devlead resume && grep -q "Auto-generated by DevLead" devlead_docs/_resume.md
- [ ] TTO-038: Resume shows convergence per BO (weight: 15) [functional]
  verify: grep -q "convergence" devlead_docs/_resume.md
- [ ] TTO-039: Resume shows next TTOs to implement (weight: 20) [functional]
  verify: grep -q "Next TTOs" devlead_docs/_resume.md
- [ ] TTO-040: Resume includes last session's key events from audit log (weight: 20) [functional]
  verify: grep -q "audit" devlead_docs/_resume.md
- [ ] TTO-041: SessionStart hook injects resume summary so LLM reads it first (weight: 20) [functional]
  verify: echo '{}' | devlead gate SessionStart 2>&1 | grep -q "DevLead"

#### TBO-010: DevLead catches its own mistakes (weight: 30)
User can: trust that when DevLead finds an inconsistency, it proposes a fix — not a speech

- [ ] TTO-042: Self-correction: hierarchy inconsistent with foundations page → auto-propose TTO (weight: 30) [functional]
  verify: echo "not yet built"
- [ ] TTO-043: K_INCONSISTENCY KPI: count of times Claude was found inconsistent and self-corrected (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-044: devlead doctor command runs coherence checks across all files (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-045: Stale _aware_*.md detected and flagged in dashboard (weight: 20) [functional]
  verify: echo "not yet built"

#### TBO-011: Works with every LLM tool (weight: 30)
User can: use DevLead with Claude, Gemini, Cursor, Codex — same governance

- [ ] TTO-046: devlead init --llm gemini generates AGENTS.md (weight: 20) [functional]
  verify: echo "not yet built"
- [ ] TTO-047: devlead init --llm cursor generates .cursorrules (weight: 20) [functional]
  verify: echo "not yet built"
- [ ] TTO-048: devlead init --llm generic generates universal AGENTS.md (weight: 20) [functional]
  verify: echo "not yet built"
- [ ] TTO-049: MD-only tier works without pip install (weight: 20) [functional]
  verify: test -f devlead_docs/_routing_table.md && test -f devlead_docs/_resume.md
- [ ] TTO-050: Tested: Gemini CLI follows routing table for R2 (weight: 20) [functional]
  verify: echo "requires manual Gemini test"

### BO-004: DevLead pays for itself (weight: 25)
- **Acceptance:** 10+ paying users. Users stay because DevLead saves them from wasted sessions and token burn. Tokenomics report proves ROI.
- **start_date:** 2026-05-01
- **end_date:** 2026-05-15
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-012: One-command install that just works (weight: 25)
User can: go from zero to governed in 60 seconds

- [ ] TTO-051: pip install devlead on Windows/Mac/Linux (weight: 25) [functional]
  verify: pip show devlead 2>&1 | grep -q "Version"
- [ ] TTO-052: devlead init creates everything in one shot (weight: 25) [functional]
  verify: mkdir -p /tmp/dit && devlead init /tmp/dit && test -f /tmp/dit/CLAUDE.md && rm -rf /tmp/dit
- [ ] TTO-053: Idempotent — re-run doesn't break anything (weight: 25) [functional]
  verify: mkdir -p /tmp/dit2 && devlead init /tmp/dit2 && devlead init /tmp/dit2 && rm -rf /tmp/dit2
- [ ] TTO-054: Published on PyPI + Claude Code marketplace (weight: 25) [functional]
  verify: echo "requires publishing"

#### TBO-013: Documentation a non-coder can follow (weight: 25)
User can: understand DevLead and start using it without help

- [ ] TTO-055: README — "Claude says done. Was it?" + 3-step install (weight: 25) [non-functional]
  verify: test -f README.md && grep -q "Claude says done" README.md
- [ ] TTO-056: User guide with walkthrough (weight: 25) [non-functional]
  verify: test -f docs/USER_GUIDE.md
- [ ] TTO-057: Example session showing DevLead catching Claude fudging (weight: 25) [non-functional]
  verify: test -f docs/example-session.md
- [ ] TTO-058: Foundations page explains architecture visually (weight: 25) [non-functional]
  verify: test -f docs/devlead-foundations.html

#### TBO-014: Proof it works — real users validate (weight: 25)
User can: see that other people use DevLead and it helped them

- [ ] TTO-059: 5 beta users install on real projects (weight: 25) [functional]
  verify: echo "requires beta program"
- [ ] TTO-060: Each beta user runs 3+ sessions with reports (weight: 25) [functional]
  verify: echo "requires beta data"
- [ ] TTO-061: Iterate on friction within 48 hours (weight: 25) [functional]
  verify: echo "requires feedback tracking"
- [ ] TTO-062: 3 testimonials collected (weight: 25) [non-functional]
  verify: echo "requires user feedback"

#### TBO-015: Pricing and distribution (weight: 25)
User can: find DevLead, understand what they pay for, and feel it's worth it

- [ ] TTO-063: Free tier: MD-only governance (weight: 20) [non-functional]
  verify: echo "requires pricing page"
- [ ] TTO-064: Paid tier: Python-enhanced with KPIs + reports + hooks (weight: 20) [non-functional]
  verify: echo "requires pricing page"
- [ ] TTO-065: GitHub repo public (weight: 20) [non-functional]
  verify: test -f LICENSE && test -f README.md
- [ ] TTO-066: Launch on 3 communities (weight: 20) [non-functional]
  verify: echo "requires Nitin to post"
- [ ] TTO-067: Tokenomics report shows ROI — users see savings (weight: 20) [functional]
  verify: devlead kpi 2>&1 | grep -q "Tokenomics"

---

## Sprint 2 — DevLead at Scale

### BO-005: Multi-project portfolio management (weight: 50)
- **Acceptance:** User running 5+ projects sees unified portfolio view, cross-project insights, and rollover between sprints.
- **start_date:** (not started)
- **end_date:** (not set)
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-016: Portfolio workspace (weight: 35)
User can: see all projects in one dashboard

- [ ] TTO-068: Portfolio config — register projects in ~/.devlead/portfolio.toml (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-069: devlead portfolio status — convergence across all projects (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-070: Portfolio dashboard — unified HTML with per-project tabs (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-071: Cross-project token comparison (weight: 25) [functional]
  verify: echo "not yet built"

#### TBO-017: Cross-project collaboration (weight: 30)
User can: share decisions and patterns between projects

- [ ] TTO-072: .collab/ INBOX/OUTBOX for cross-project messaging (weight: 35) [functional]
  verify: echo "not yet built"
- [ ] TTO-073: Shared decision promotion across projects (weight: 35) [functional]
  verify: echo "not yet built"
- [ ] TTO-074: Cross-project dependency tracking (weight: 30) [functional]
  verify: echo "not yet built"

#### TBO-018: Sprint rollover (weight: 35)
User can: close a sprint, archive done work, carry forward open items

- [ ] TTO-075: devlead rollover archives done BOs/TTOs (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-076: Open TTOs carry to next sprint with context (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-077: Auto-generated sprint retrospective from KPI trends (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-078: Historical sprint view (weight: 25) [functional]
  verify: echo "not yet built"

### BO-006: DevLead becomes the standard (weight: 50)
- **Acceptance:** Recognized as THE governance tool for AI-assisted development. Enterprise features. Competitive moat.
- **start_date:** (not started)
- **end_date:** (not set)
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-019: Enterprise (weight: 35)
User can: use DevLead with teams and integrations

- [ ] TTO-079: Team roles — who can mark done, who revises deadlines (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-080: Approval workflows for TBO completion (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-081: GitHub Issues/PR integration (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-082: Linear/Jira sync (weight: 25) [functional]
  verify: echo "not yet built"

#### TBO-020: Advanced governance (weight: 35)
User can: build sophisticated custom rules

- [ ] TTO-083: Custom responsibilities — user-defined R7, R8 (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-084: Budget controls — token limit per BO (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-085: Quality gates — TBO blocked until predecessor completes (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-086: Automated retrospectives from KPI trends (weight: 25) [functional]
  verify: echo "not yet built"

#### TBO-021: Analytics and intelligence (weight: 30)
User can: see predictions and patterns

- [ ] TTO-087: Velocity prediction — when will this BO finish? (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-088: LLM comparison — which model performs better? (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-089: Anomaly detection — flag sessions with convergence drops (weight: 25) [functional]
  verify: echo "not yet built"
- [ ] TTO-090: Weekly digest email (weight: 25) [non-functional]
  verify: echo "not yet built"
