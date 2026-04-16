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
> TTO checkboxes are ONLY checked by DevLead verification, NEVER by Claude.
> Functional TTOs have verify: commands. Non-functional TTOs can be marked by Claude.

---

## Sprint 1 — DevLead v2: From Concept to $1000/month

### BO-001: DevLead is a well-rounded robust product (weight: 35)
- **Acceptance:** A non-coder installs DevLead, works with any LLM for 5 sessions, and at the end of each session can open one HTML page that tells them the truth about what happened. The LLM follows the routing table without being reminded. Zero dark code.
- **start_date:** 2026-04-16
- **end_date:** 2026-04-25
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-001: Intent routing works end-to-end (weight: 25)
User can: say anything and DevLead routes it correctly or stays out of the way

- [ ] TTO-001: Routing table embedded in CLAUDE.md with all responsibilities (weight: 15) [functional]
  verify: grep -q "## R1" CLAUDE.md && grep -q "## R2" CLAUDE.md && grep -q "## R4" CLAUDE.md && grep -q "## R5" CLAUDE.md && grep -q "## R6" CLAUDE.md
- [ ] TTO-002: Fresh session test — Claude follows R2 when asked to code without focus (weight: 25) [functional]
  verify: echo "requires fresh session test by Nitin"
- [ ] TTO-003: Fresh session test — Claude follows R1 when asked to add a feature (weight: 25) [functional]
  verify: echo "requires fresh session test by Nitin"
- [ ] TTO-004: AGENTS.md generated for Gemini CLI with same routing table (weight: 15) [functional]
  verify: test -f AGENTS.md && grep -q "## R1" AGENTS.md
- [ ] TTO-005: Intent classification handles ambiguous inputs gracefully (weight: 10) [functional]
  verify: echo "requires fresh session test by Nitin"
- [ ] TTO-006: Adding R7 responsibility = add markdown section, zero code change (weight: 10) [functional]
  verify: grep -q "To add a new responsibility" devlead_docs/_routing_table.md

#### TBO-002: Work pipeline captures everything from idea to done (weight: 20)
User can: go from "I have an idea" to tracked, prioritized, decomposed work

- [ ] TTO-007: Scratchpad capture preserves raw user input verbatim (weight: 15) [functional]
  verify: python -c "from devlead.scratchpad import append_entry, iter_untriaged; from pathlib import Path; append_entry(Path('/tmp/sp.md'),'test','body'); assert len(iter_untriaged(Path('/tmp/sp.md')))>0" && rm /tmp/sp.md
- [ ] TTO-008: Triage routes to 3 targets — work, decision, fact (weight: 15) [functional]
  verify: grep -q "intake" src/devlead/cli.py && grep -q "decision" src/devlead/cli.py && grep -q "fact" src/devlead/cli.py
- [ ] TTO-009: Intake ingest from scratchpad with bidirectional trace (weight: 15) [functional]
  verify: python -c "from devlead.bridge import ingest_from_scratchpad; print('importable')"
- [ ] TTO-010: Intake to hierarchy promotion command (weight: 25) [functional]
  verify: devlead promote --help 2>&1 | grep -q "hierarchy" || echo "not yet built"
- [ ] TTO-011: Hierarchy convergence computed from real checkbox state (weight: 15) [functional]
  verify: python -c "from devlead.hierarchy import parse; from pathlib import Path; s=parse(Path('devlead_docs/_project_hierarchy.md')); assert len(s)>0; print(f'{s[0].convergence:.1f}%')"
- [ ] TTO-012: Definition of Done — verify: commands run by DevLead, not Claude (weight: 15) [functional]
  verify: grep -c "verify:" devlead_docs/_project_hierarchy.md | grep -q "[2-9][0-9]"

#### TBO-003: Session report is the single source of trust (weight: 20)
User can: open one HTML file and know whether Claude lied

- [ ] TTO-013: Report checks all installed files exist (weight: 10) [functional]
  verify: devlead report && grep -q "Installation health" docs/session-report-*.html
- [ ] TTO-014: Report runs every command and shows pass/fail (weight: 15) [functional]
  verify: grep -q "Command health" docs/session-report-*.html
- [ ] TTO-015: Report shows KPIs from real data (weight: 15) [functional]
  verify: grep -q "KPIs" docs/session-report-*.html
- [ ] TTO-016: Report shows hierarchy convergence per BO (weight: 10) [functional]
  verify: grep -q "convergence" docs/session-report-*.html
- [ ] TTO-017: Report runs verify: commands from hierarchy and shows results (weight: 25) [functional]
  verify: grep -q "Definition of Done" docs/session-report-*.html
- [ ] TTO-018: Report shows token usage per session (weight: 10) [functional]
  verify: grep -q "oken" docs/session-report-*.html
- [ ] TTO-019: Stop hook auto-generates report + resume at session end (weight: 15) [functional]
  verify: grep -q "Stop" .claude/settings.json

#### TBO-004: KPI engine computes truth from data (weight: 15)
User can: see 25 metrics that are computed, never estimated

- [ ] TTO-020: 25 KPIs across 4 categories all compute without error (weight: 30) [functional]
  verify: devlead kpi 2>&1 | grep -c ":" | awk '{exit ($1 >= 15 ? 0 : 1)}'
- [ ] TTO-021: Tokenomics KPI tracks cost-per-convergence-point (weight: 25) [functional]
  verify: devlead kpi 2>&1 | grep -q "Tokenomics"
- [ ] TTO-022: Session history records convergence + tokens per session (weight: 25) [functional]
  verify: python -c "from devlead.kpi import record_session; from pathlib import Path; record_session(Path('devlead_docs'), 1000); print('ok')"
- [ ] TTO-023: K_BYPASS tracks discipline violations as a trend (weight: 20) [functional]
  verify: devlead kpi 2>&1 | grep -q "K_BYPASS"

#### TBO-005: Session continuity — zero context loss between sessions (weight: 20)
User can: close the CLI, reopen tomorrow, and Claude picks up exactly where it left off

- [ ] TTO-024: _resume.md auto-generated from hierarchy + intake + audit + git (weight: 20) [functional]
  verify: devlead resume && grep -q "Auto-generated by DevLead" devlead_docs/_resume.md
- [ ] TTO-025: Resume shows next TTOs to implement with parent BO/TBO (weight: 15) [functional]
  verify: grep -q "Next TTOs" devlead_docs/_resume.md
- [ ] TTO-026: Resume shows hierarchy convergence (weight: 15) [functional]
  verify: grep -q "Hierarchy convergence" devlead_docs/_resume.md
- [ ] TTO-027: SessionStart hook injects context so LLM reads resume first (weight: 20) [functional]
  verify: echo '{}' | devlead gate SessionStart 2>&1 | grep -q "resume"
- [ ] TTO-028: All governance content embedded in CLAUDE.md, not in separate files LLM might skip (weight: 15) [functional]
  verify: wc -l CLAUDE.md | awk '{exit ($1 > 100 ? 0 : 1)}'
- [ ] TTO-029: Fresh session test — Claude reads resume and knows what to do without being told (weight: 15) [functional]
  verify: echo "requires fresh session test by Nitin"

### BO-002: DevLead installs in 60 seconds and just works (weight: 25)
- **Acceptance:** A non-coder with zero setup runs one command and gets a governed project. Works on Windows, Mac, Linux. Works with Claude Code, Gemini CLI, Cursor.
- **start_date:** 2026-04-25
- **end_date:** 2026-05-01
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-006: One-command install (weight: 35)
User can: type one command and have governance active

- [ ] TTO-030: pip install devlead works on clean machine (weight: 25) [functional]
  verify: pip show devlead 2>&1 | grep -q "Version"
- [ ] TTO-031: devlead init creates devlead_docs + CLAUDE.md + hooks in one shot (weight: 25) [functional]
  verify: mkdir -p /tmp/dit && devlead init /tmp/dit && test -f /tmp/dit/CLAUDE.md && test -f /tmp/dit/.claude/settings.json && rm -rf /tmp/dit
- [ ] TTO-032: devlead init detects LLM tool and generates CLAUDE.md or AGENTS.md accordingly (weight: 25) [functional]
  verify: python -c "from devlead.bootstrap import generate_section; assert len(generate_section()) > 200"
- [ ] TTO-033: Idempotent — re-running init on existing project doesn't break anything (weight: 25) [functional]
  verify: mkdir -p /tmp/dit2 && devlead init /tmp/dit2 && devlead init /tmp/dit2 && rm -rf /tmp/dit2

#### TBO-007: Works without Python (MD-only tier) (weight: 30)
User can: copy devlead_docs/ into any project and get governance without pip

- [ ] TTO-034: devlead_docs/ folder is self-contained — no Python imports needed for governance (weight: 30) [functional]
  verify: test -f devlead_docs/_routing_table.md && test -f devlead_docs/_resume.md && test -f devlead_docs/_project_hierarchy.md
- [ ] TTO-035: Template pack downloadable from GitHub as a zip (weight: 20) [non-functional]
  verify: echo "requires GitHub setup"
- [ ] TTO-036: README explains MD-only vs Python-enhanced tiers clearly (weight: 25) [non-functional]
  verify: test -f README.md && wc -l README.md | awk '{exit ($1 > 30 ? 0 : 1)}'
- [ ] TTO-037: Governance rules work when pasted into Cursor rules or Windsurf config (weight: 25) [functional]
  verify: echo "requires manual test with Cursor"

#### TBO-008: Documentation a non-coder can follow (weight: 35)
User can: read the README and know what DevLead does, why they need it, and how to start

- [ ] TTO-038: README — "Claude says done. Was it?" pitch + 3-step install + what happens next (weight: 30) [non-functional]
  verify: test -f README.md && grep -q "Claude says done" README.md
- [ ] TTO-039: User guide — "I installed DevLead, now what?" with screenshots (weight: 30) [non-functional]
  verify: test -f docs/USER_GUIDE.md && wc -l docs/USER_GUIDE.md | awk '{exit ($1 > 50 ? 0 : 1)}'
- [ ] TTO-040: Example session transcript — shows DevLead catching Claude fudging (weight: 20) [non-functional]
  verify: test -f docs/example-session.md
- [ ] TTO-041: Video or GIF showing install + first session + report (weight: 20) [non-functional]
  verify: echo "requires Nitin to create"

### BO-003: DevLead generates its first $1000/month (weight: 25)
- **Acceptance:** 10+ paying users or $1000 MRR. Users renew because DevLead saves them from wasted sessions.
- **start_date:** 2026-05-01
- **end_date:** 2026-05-15
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-009: Pricing that matches value (weight: 25)
User can: understand what they pay for and feel it's worth it

- [ ] TTO-042: Free tier: MD-only governance (routing table, hierarchy, scratchpad) (weight: 30) [non-functional]
  verify: echo "requires pricing page"
- [ ] TTO-043: Paid tier: Python-enhanced (KPIs, HTML reports, hooks, audit log) (weight: 30) [non-functional]
  verify: echo "requires pricing page"
- [ ] TTO-044: Pricing validated with 3 target users before launch (weight: 40) [functional]
  verify: echo "requires user interviews by Nitin"

#### TBO-010: Distribution — be where the users are (weight: 25)
User can: find DevLead without Nitin telling them about it

- [ ] TTO-045: Published on PyPI (weight: 20) [functional]
  verify: pip install devlead --dry-run 2>&1 | grep -q "devlead"
- [ ] TTO-046: Published on Claude Code plugin marketplace (weight: 20) [functional]
  verify: test -f .claude-plugin/plugin.json
- [ ] TTO-047: GitHub repo public with stars and README (weight: 20) [non-functional]
  verify: test -f LICENSE && test -f README.md
- [ ] TTO-048: Launch post on 3 communities (Claude Discord, AI dev Reddit, Hacker News) (weight: 20) [non-functional]
  verify: echo "requires Nitin to post"
- [ ] TTO-049: SEO — "Claude accountability" or "AI governance tool" ranks page 1 (weight: 20) [non-functional]
  verify: echo "requires time and content"

#### TBO-011: Proof it works — real users, real feedback (weight: 30)
User can: see testimonials and case studies from actual DevLead users

- [ ] TTO-050: 5 beta users install DevLead on real projects (weight: 25) [functional]
  verify: echo "requires beta program by Nitin"
- [ ] TTO-051: Each beta user runs 3+ sessions and generates reports (weight: 25) [functional]
  verify: echo "requires beta user data"
- [ ] TTO-052: Collect 3 testimonials or case studies (weight: 25) [non-functional]
  verify: echo "requires user feedback"
- [ ] TTO-053: Iterate on friction points within 48 hours of each feedback (weight: 25) [functional]
  verify: echo "requires tracking feedback->fix cycle"

#### TBO-012: Retention — users stay because DevLead saves them money (weight: 20)
User can: see that DevLead reduced their wasted sessions and token spend

- [ ] TTO-054: Tokenomics report shows before/after DevLead cost comparison (weight: 35) [functional]
  verify: devlead kpi 2>&1 | grep -q "Tokenomics"
- [ ] TTO-055: Convergence trend shows projects actually finishing (weight: 35) [functional]
  verify: devlead kpi 2>&1 | grep -q "Sprint convergence"
- [ ] TTO-056: Monthly email digest with KPI summary for paying users (weight: 30) [non-functional]
  verify: echo "requires email infrastructure"

### BO-004: DevLead eats its own dogfood (weight: 15)
- **Acceptance:** DevLead governs its own development. Every session follows the routing table. Every commit traces to a TTO. The report proves it.
- **start_date:** 2026-04-16
- **end_date:** 2026-05-15
- **actual_date:** (pending)
- **revised_date:** (none)
- **revision_justification:** (none)

#### TBO-013: DevLead develops under its own governance (weight: 50)
User can: look at DevLead's own repo and see the governance in action

- [ ] TTO-057: Every commit message references a TTO ID (weight: 25) [functional]
  verify: git log --oneline -10 | grep -c "TTO-" | awk '{exit ($1 >= 5 ? 0 : 1)}'
- [ ] TTO-058: _audit_log.jsonl has real events from real sessions (weight: 25) [functional]
  verify: wc -l devlead_docs/_audit_log.jsonl | awk '{exit ($1 > 10 ? 0 : 1)}'
- [ ] TTO-059: Session reports exist for every development session (weight: 25) [functional]
  verify: ls docs/session-report-*.html | wc -l | awk '{exit ($1 >= 3 ? 0 : 1)}'
- [ ] TTO-060: K_BYPASS rate trends downward over sessions (weight: 25) [functional]
  verify: echo "requires 3+ sessions of history"

#### TBO-014: DevLead's own hierarchy is the product demo (weight: 50)
User can: see DevLead's BO/TBO/TTO tree as proof the system works

- [ ] TTO-061: Hierarchy has 4+ BOs with real deadlines (weight: 25) [functional]
  verify: grep -c "^### BO-" devlead_docs/_project_hierarchy.md | awk '{exit ($1 >= 4 ? 0 : 1)}'
- [ ] TTO-062: Convergence percentage is computed and displayed in report (weight: 25) [functional]
  verify: devlead kpi 2>&1 | grep -q "Sprint convergence"
- [ ] TTO-063: At least one BO has been completed and marked with actual_date (weight: 25) [functional]
  verify: grep -q "actual_date: 2026" devlead_docs/_project_hierarchy.md
- [ ] TTO-064: Change management triggered on at least one missed deadline (weight: 25) [functional]
  verify: grep -q "revised_date: 2026" devlead_docs/_project_hierarchy.md
