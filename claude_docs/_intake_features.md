# Feature Intake

> Type: INTAKE
> Last updated: 2026-04-05 | Open: 15 | Closed: 0

## Active

| Key | Item | Source | Added | Status | Priority | Notes |
|-----|------|--------|-------|--------|----------|-------|
| FEAT-001 | Token usage KPIs — cost per task, wasted tokens, efficiency | user | 2026-04-05 | OPEN | P3 | V2 — needs Claude transcript_path from hook input |
| FEAT-002 | Claude Workflow hooks — governance for scheduled agents | user | 2026-04-05 | OPEN | P3 | V2 — pre/post workflow gates, DoD for scheduled tasks |
| FEAT-003 | Rollover policy — by date OR by file size (lines threshold) | user | 2026-04-05 | OPEN | P2 | Config: rollover_trigger = "date" or "size", max_lines = 500 |
| FEAT-004 | Cross-project guard — user-level hook protects all DevLead projects | user | 2026-04-05 | OPEN | P1 | `devlead install-guard` sets up ~/.claude/settings.json hook. Prevents ungoverned edits from other sessions. |
| FEAT-005 | File path enforcement in gate — inspect stdin JSON for target path | user | 2026-04-05 | OPEN | P1 | Gate checks WHERE files are written, not just IF. Blocks memory writes outside UPDATE, enforces naming convention. |
| FEAT-006 | Session-end HTML dashboard — beautiful local report with all KPIs, project updates, stats | user | 2026-04-05 | OPEN | P1 | Generated when session ends. Clickable, dashboard-style. Every detail: KPIs, audit log, tasks done, state transitions, intake changes. |
| FEAT-007 | Token usage auditing — full capability for tracking, waste detection, best practices | user | 2026-04-05 | OPEN | P1 | Read transcript_path from hook stdin. Detect wasteful patterns: repeated image attachments, large context, bad prompts. Show cost per task, wasted tokens, efficiency recommendations. Include in HTML dashboard. |
| FEAT-008 | Scope lock — user defines surgical focus for what LLM must work on | user | 2026-04-05 | OPEN | P1 | User specifies allowed files, directories, or approach before EXECUTE. Gate enforces scope — blocks edits outside allowed paths. Prevents AI from wandering into wrong files or reworking things not asked for. Could be `devlead scope set src/devlead/audit.py src/devlead/cli.py` or a scope section in the plan. |
| FEAT-009 | Record model name everywhere — audit log, session history, HTML dashboard | user | 2026-04-05 | OPEN | P2 | Users choose models (Claude, GPT, Copilot). Record which model was used in every audit entry and session. Enables per-model KPI comparison (which model wastes more tokens, which has better FTR). |
| FEAT-010 | API key / license management — free vs Pro tier gating | user | 2026-04-05 | OPEN | P1 | Validate license key for Pro features (portfolio, collab). Free tier = 1 project, full features. Pro = unlimited projects. Key stored locally, no server call. |
| FEAT-011 | HTML dashboard → markdown updates — interactive edits from browser | user | 2026-04-05 | OPEN | P2 | Basic update forms in HTML dashboard that write back to allowed claude_docs/ MD files. E.g., mark a task DONE, close an intake item, add a note. Local file writes only. |
| FEAT-012 | GitHub open-source packaging — LICENSE, proper README, PyPI distribution | user | 2026-04-05 | OPEN | P1 | MIT license, proper README.md, setup for PyPI distribution. Make repo presentable for open-source. |
| FEAT-013 | Portfolio dashboard — multi-project view with project selector | user | 2026-04-05 | OPEN | P2 | Dashboard should handle portfolio context. Project selector at top, cross-project stats, per-project drill-down. Hierarchy: Portfolio → Project → Epic → Story → Task. |
| FEAT-014 | Progress timeline — only TBO milestones and productionization | user | 2026-04-05 | OPEN | P1 | Trends timeline tracks ONLY TBO status changes and distribution milestones. Technical work (stories/tasks) is shadow work — work that doesn't contribute to any TBO is shadow work in hindsight. Timeline should be sparse: each entry = a TBO moved. |
| FEAT-015 | Split dashboard.py into smaller modules | user | 2026-04-05 | OPEN | P2 | dashboard.py is 1200+ lines. Split into: dashboard_html.py (CSS/wrapper), dashboard_tabs.py (tab builders), dashboard_helpers.py (formatting). Keep each under ~200 lines. |

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|
