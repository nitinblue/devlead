# DevLead Setup Guide

> Lead your development. Don't let AI wander.

## What is DevLead?

DevLead is a governance layer for AI-assisted development. It ensures every piece of work traces to a business outcome, every task has a ticket, and nothing happens without prioritization.

It works as a Claude Code plugin via hooks -- enforcing process without blocking creativity.

## Prerequisites

- Python 3.11+
- Claude Code (CLI, desktop app, or IDE extension)
- Git

## Installation

### From GitHub (current method)

```bash
git clone https://github.com/your-username/devlead.git
cd devlead
pip install -e .
```

### From another project (local development)

If you have DevLead checked out locally and want to use it in a different project:

```bash
pip install -e /path/to/devlead
```

The `-e` flag means editable -- changes to DevLead source are immediately available without reinstalling.

### From PyPI (coming soon)

```bash
pip install devlead
```

### As a Claude Code Plugin (target state)

Once DevLead is published as a Claude Code plugin:

```
/plugin install devlead
```

No pip install, no manual setup. The plugin auto-bootstraps on first session.

### Verify installation

```bash
devlead --help
devlead --version
```

## Setting Up a New Project

### 1. Initialize

Navigate to your project root and run:

```bash
cd /path/to/your-project
devlead init
```

This creates:
- `devlead_docs/` -- governance files (tasks, roadmap, stories, intake, standing instructions)
- `devlead.toml` -- project configuration
- `.claude/settings.json` -- Claude Code hooks for enforcement

### 2. Define Your Business Outcomes

Open `devlead_docs/_living_business_objectives.md` and define your TBOs (Tangible Business Outcomes).

TBOs answer: "What can the user do now that they couldn't before?"

```markdown
| ID | Objective | Linked Stories | Status | Planned | Actual | Metric |
|----|-----------|---------------|--------|---------|--------|--------|
| TBO-1 | Users can place live trades on India market | S-001, S-002 | OPEN | 2026-04-15 | -- | Trade executes, confirms, shows in portfolio |
| TBO-2 | Users can place live trades on US market | S-003, S-004 | OPEN | 2026-04-30 | -- | Same as TBO-1 but for US equities |
```

### 3. Create Stories

Open `devlead_docs/_project_stories.md` and link each story to a TBO:

```markdown
| ID | Story | Epic | TBO Link | Status | DoD | Risks | Dependencies |
|----|-------|------|----------|--------|-----|-------|--------------|
| S-001 | Broker connection for India | E-001 | TBO-1 | OPEN | Broker API authenticated, orders submit | API rate limits | None |
| S-002 | Order execution engine | E-001 | TBO-1 | OPEN | Market/limit orders execute within 2s | Latency | S-001 |
```

### 4. Start Using with Claude

No need to run `devlead start` manually -- the SessionStart hook does it automatically when Claude Code opens your project.

The session flow is:

```
SESSION_START -> ORIENT -> TRIAGE -> PRIORITIZE -> PLAN -> EXECUTE -> UPDATE -> SESSION_END
```

**ORIENT** -- Read project docs, scan intake, report KPIs
**TRIAGE** -- Review scratchpad items, accept or archive each one
**PRIORITIZE** -- Assign priorities, pick what to work on this session
**PLAN** -- Design the approach before writing code
**EXECUTE** -- Write code (requires an IN_PROGRESS task in the book of work)
**UPDATE** -- Update project docs, intake, status

## Setting Up an Existing Project

If your project already has markdown files, use migrate instead of init:

```bash
cd /path/to/existing-project
devlead migrate --dry-run    # preview what will be created
devlead migrate              # create missing governance files
```

DevLead will:
- Scan for existing governance files (markdown in root, docs/, devlead_docs/)
- Create only what's missing -- never overwrites existing files
- Merge hooks into `.claude/settings.json` for enforcement
- Append a DevLead governance section to `CLAUDE.md` (so Claude reads devlead_docs/ on session start)
- Update `.gitignore` to exclude session state
- Log all migration actions to `devlead_docs/_audit_log.jsonl`
- Generate a migration report showing what was found and what was created

After migration, work with Claude to:
1. Map your existing work items to TBOs
2. Link stories to TBOs
3. Assign tasks to stories

## Key Commands

| Command | What it does |
|---------|-------------|
| `devlead init` | Initialize a new project |
| `devlead migrate` | Bootstrap DevLead on an existing project |
| `devlead migrate --dry-run` | Preview migration without writing files |
| `devlead start` | Start a session (auto-called by SessionStart hook) |
| `devlead status` | Show current state and KPIs |
| `devlead view` | Full TBO -> Story -> Task hierarchy |
| `devlead analyze` | Smart project analysis by business outcome |
| `devlead report` | Session report from md files |
| `devlead gap` | Detect governance gaps |
| `devlead dashboard` | Generate HTML dashboard |
| `devlead triage` | Show pending scratchpad items |
| `devlead triage SCRATCH-001 feature P1` | Classify a scratchpad item |
| `devlead scratch add "idea"` | Capture an idea in scratchpad |
| `devlead effort` | Show token/session effort per task |
| `devlead effort TASK-045` | Show effort for a specific task |
| `devlead doctor` | Diagnose project health |
| `devlead healthcheck` | Same as doctor |
| `devlead gate EXECUTE` | Check if current state allows editing |
| `devlead transition PLAN` | Move to next state |
| `devlead checklist ORIENT status_read` | Mark checklist item done |
| `devlead kpis` | Show project KPIs |
| `devlead scope set src/file.py` | Lock edits to specific files |
| `devlead scope show` | Show current scope lock |
| `devlead scope clear` | Remove scope lock |
| `devlead audit` | Show governance audit log |
| `devlead rollover` | Archive completed work |
| `devlead portfolio add /path` | Register project in portfolio |
| `devlead portfolio list` | List all portfolio projects |
| `devlead collab status` | Cross-project collaboration status |

## How Enforcement Works

DevLead hooks into Claude Code via `.claude/settings.json`:

- **SessionStart** -- `devlead start` initializes session, transitions to ORIENT
- **Before any file edit (Edit/Write)** -- checks you're in EXECUTE state and have an IN_PROGRESS task
- **Before plan mode (EnterPlanMode)** -- checks you're in PRIORITIZE or EXECUTE state
- **After plan mode (ExitPlanMode)** -- auto-transitions to EXECUTE
- **On session end (Stop)** -- generates a session report and dashboard

Hard blocks (cannot bypass):
- No file edits outside EXECUTE or UPDATE state
- No file edits without an IN_PROGRESS task ticket
- Memory writes only during UPDATE state
- State transitions blocked until checklist is complete

Guide with override (recommended but skippable):
- TRIAGE before PRIORITIZE
- PRIORITIZE before PLAN
- State machine flow

### Known Limitations

- Bash tool writes (e.g., `sed -i`) are not gated -- only Edit/Write tool calls are intercepted by hooks. This is a Claude Code hook limitation; the Bash matcher is too broad and blocks all bash commands including reads.

## Configuration

Edit `devlead.toml` in your project root:

```toml
[project]
name = "my-project"
docs_dir = "devlead_docs"

[governance]
task_required = "block"       # "log", "warn", "block"
memory_from_docs = "block"    # memory writes only in UPDATE
intake_required = "warn"      # intake files must exist

[paths]
docs_policy = "warn"          # "log", "warn", "block" for devlead_docs/ edits outside UPDATE

[kpis]
circles_warning = 50
ftr_minimum = 60
convergence_target = 80

[rollover]
trigger = "date"
day_of_month = 1
max_lines = 500
```

## The Hierarchy

Everything traces upward:

```
Task (implementation unit)
  -> Story (technical deliverable, has Definition of Done)
    -> TBO (business outcome -- what the user can do)
```

- A Task without a Story = **shadow work**
- A Story without a TBO = **shadow work**
- Progress = TBOs completed, not tasks completed
- Convergence = TBOs done / TBOs total

## HTML Dashboard

```bash
devlead dashboard
```

Opens a visual report with tabs:
- **Business** -- TBO convergence, timeline with Gantt chart
- **Overview** -- Project stats at a glance
- **Roadmap** -- TBO -> Story -> Task with collapsible stories, tokens, duration
- **KPIs** -- Project health metrics
- **Trends** -- Session-over-session changes
- **Backlog** -- Scratchpad + open FEAT/BUG/GAP items by priority
- **Session** -- Current session state and transitions
- **Audit** -- Governance actions (doc updates, config changes)
- **Productionize** -- Distribution milestones and funnel

The dashboard auto-regenerates on state transitions and when you run `devlead view` or `devlead report`.

## File Structure

After initialization, your project will have:

```
your-project/
├── devlead_docs/                         # System of record
│   ├── _project_status.md                # Current project state
│   ├── _project_tasks.md                 # Task backlog
│   ├── _project_roadmap.md               # Epics and stories
│   ├── _project_stories.md               # Stories with TBO linkage
│   ├── _intake_features.md               # Feature requests
│   ├── _intake_bugs.md                   # Bug reports
│   ├── _intake_gaps.md                   # Governance gaps
│   ├── _intake_issues.md                 # General issues
│   ├── _living_standing_instructions.md  # Standing rules
│   ├── _living_business_objectives.md    # TBOs
│   ├── _living_distribution.md           # Distribution milestones
│   ├── _scratchpad.md                    # Quick capture before triage
│   ├── _audit_log.jsonl                  # Governance audit trail
│   ├── _effort_log.jsonl                 # Token/time tracking
│   ├── session_state.json                # Current session (gitignored)
│   ├── session_history.jsonl             # Session snapshots
│   └── dashboard_YYYY-MM-DD.html         # Generated report
├── devlead.toml                          # Configuration
├── .claude/settings.json                 # Claude Code hooks
└── CLAUDE.md                             # Project instructions
```

## Workflow Example

```
1. Claude starts a session (SessionStart hook auto-calls devlead start)
2. DevLead enters ORIENT -- Claude reads project docs and reports KPIs
3. Transition to TRIAGE -- review scratchpad items
4. Transition to PRIORITIZE -- pick tasks for this session
5. Transition to PLAN -- design approach (enter plan mode)
6. Exit plan mode -> auto-transition to EXECUTE
7. Write code (gate checks: EXECUTE state + IN_PROGRESS task)
8. Transition to UPDATE -- update docs, tasks, intake
9. Session ends (Stop hook -> devlead report + dashboard)
```
