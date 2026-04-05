# DevLead — Design Spec

> **Lead your development. Don't let AI wander.**
> Date: 2026-04-05
> Status: DRAFT
> Author: Nitin Jain + Claude

---

## 1. Problem

AI coding assistants (Claude Code, Copilot, Cursor) have made development faster. But faster is not the same as forward.

Teams using AI assistants face a new category of problem — **development without governance:**

- **The AI writes code, but doesn't know WHY.** It produces features without understanding which business objective they serve. You get velocity without direction.
- **The AI skips planning.** Given a request, it jumps to code. No orientation. No requirements capture. No plan approval. The result: ad-hoc changes that create tech debt.
- **The AI doesn't learn.** Each session starts from zero. Mistakes repeat. The same rework cycles happen week after week. There's no feedback loop.
- **The AI goes rogue.** It invents objectives. It deviates from approved plans. It says "I hear you" but doesn't change behavior. Instructions in markdown are suggestions it can ignore.
- **Nobody tracks AI effectiveness.** How much rework did the AI cause? Did it follow the plan? Is it getting better? There are no KPIs for AI-assisted development.

**Result:** Developers spend money on AI tools but can't launch products. They go in circles — writing code, reworking code, never converging on business objectives. The AI is fast but undirected. The project moves, but not forward.

## 2. Solution

DevLead is **project governance for AI-assisted development.** It doesn't manage your project. It governs the development phase — ensuring that every AI session is disciplined, plan-driven, and aligned with business objectives.

**What DevLead does:**

- **Enforces a development lifecycle.** A state machine controls the session: orient (understand where you are) → intake (capture what needs doing) → plan (design the approach) → execute (write code) → update (record what happened). The AI cannot skip steps.
- **Blocks unauthorized actions.** Hooks physically prevent code edits outside the plan phase. The AI literally cannot go rogue — the gate won't open.
- **Tracks AI effectiveness with KPIs.** 23 built-in metrics across LLM effectiveness, delivery, and project health. Is the AI getting better? Is work converging on objectives? Is the AI going in circles?
- **Maintains a living document model.** 4 file types (`_living`, `_intake`, `_project`, user profile) ensure all project knowledge is in-repo, team-visible, and traceable. No hidden state.
- **Recommends what to work on next — and WHY.** Every recommendation ties to a business objective. "Work on TASK-045 because it advances Go-Live US from 3/12 to 4/12."

**What DevLead is NOT:**

- Not a deployment/shipping tool
- Not a CI/CD pipeline
- Not a PM tool (no Jira, no Linear, no sprint ceremonies)
- Not an AI coding tool — it governs AI coding tools

DevLead is the governance layer that was missing between "we have an AI assistant" and "we're actually delivering business outcomes."

## 3. Target User

Dev teams of 2-10 people using AI coding assistants (starting with Claude Code). They've experienced the problem firsthand: the AI is productive but not effective. Code gets written but products don't ship. They want structure without bureaucracy — governance that runs automatically via hooks, not process that requires manual discipline.

## 4. Revenue Model

**Freemium with one-time upgrade.**

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | 1 project. Full state machine, hooks, all 23 KPIs, doc model, rollover. No limits on features. |
| **Pro** | $49 one-time | Unlimited projects. Portfolio dashboard, cross-project KPIs, cross-project dependencies, unified "Next Best Action" across projects. |

**Why this works:**
- Free tier is genuinely useful — not crippled. A solo dev with one project gets everything.
- The moment you have 2+ projects (which is most teams), you need the portfolio view. That's the natural upgrade trigger.
- One-time, not subscription. Developer buys it, owns it. No recurring revenue headache for the buyer.
- Distribution via Gumroad, GitHub Sponsors, or PyPI (free tier on PyPI, Pro via license key).

### 4.1 Installation

```bash
# From PyPI (public, free tier or paid via license key)
pip install devlead

# From downloaded zip (paid, via Gumroad)
pip install ./devlead-1.0.0.tar.gz

# Development install
pip install -e .
```

After install, the `devlead` CLI is available system-wide. No runtime dependencies beyond Python 3.11+.

### 4.2 Upgrade

```bash
pip install --upgrade devlead
```

Upgrades replace only the engine code. `claude_docs/` files in the target project are never touched by upgrades — the user owns those files after `devlead init`.

### 4.3 Uninstall

```bash
pip uninstall devlead
```

This removes the CLI. The `claude_docs/` folder and all project docs remain untouched — they are plain markdown, readable without DevLead. The hooks in `.claude/settings.json` will show errors (command not found) and should be manually removed.

## 5. Architecture

### 5.1 Package Structure

```
src/devlead/
├── __init__.py               # Version, metadata
├── cli.py                    # CLI entry point
├── state_machine.py          # States, transitions, gates, checklists
├── kpi_engine.py             # KPI computation from project docs
├── doc_parser.py             # Parse _living/_intake/_project markdown files
├── rollover.py               # Monthly archival logic
├── hooks.py                  # Hook JSON output (allow/block/context)
├── config.py                 # Read/validate devlead.toml
└── scaffold/                 # Templates for `devlead init`
    ├── claude_operatingmodel.md
    ├── _living_standing_instructions.md
    ├── _intake_bugs.md
    ├── _intake_features.md
    ├── _intake_gaps.md
    ├── _intake_changes.md
    ├── _project_status.md
    ├── _project_tasks.md
    ├── _project_roadmap.md
    └── hooks_settings.json
```

### 5.2 Components

| Component | Responsibility | Dependencies |
|-----------|---------------|-------------|
| `cli.py` | Parse commands, dispatch to modules | All modules |
| `state_machine.py` | State tracking, transitions, gate checks, exit criteria | `hooks.py` for output |
| `kpi_engine.py` | Compute KPIs from project docs | `doc_parser.py` |
| `doc_parser.py` | Parse markdown tables, count items, extract metadata | None (stdlib only) |
| `rollover.py` | Archive monthly, carry forward open items | `doc_parser.py` |
| `hooks.py` | Format JSON output for Claude Code hooks (exit codes) | None |
| `config.py` | Read `devlead.toml`, provide defaults | None (stdlib + tomllib) |

### 5.3 No External Dependencies

DevLead uses **only Python stdlib**. No pip dependencies. This matters:
- Faster install
- No dependency conflicts with host project
- Works in any Python 3.11+ environment
- `tomllib` is stdlib since 3.11

## 6. State Machine

### 6.1 States

```
SESSION_START → ORIENT → INTAKE → PLAN → EXECUTE → UPDATE → SESSION_END
```

| State | Purpose | Entry Criteria | Exit Criteria |
|-------|---------|---------------|---------------|
| SESSION_START | Hook fires, initialize | Session begins | State file created |
| ORIENT | Read project state, report KPIs | State file exists | Status read, tasks read, intake scanned, KPIs reported |
| INTAKE | Capture requests, triage | ORIENT complete | Requests in _intake, triaged to _project_tasks |
| PLAN | Enter plan mode, design | INTAKE complete | Plan approved (ExitPlanMode) |
| EXECUTE | Write code, run tests | Plan approved | Deliverables met, tests pass |
| UPDATE | Update all docs | EXECUTE complete | Intake closed, tasks updated, status updated, living reviewed, memory derived |
| SESSION_END | Final report | UPDATE complete | Memory regenerated |

### 6.2 Valid Transitions

```
SESSION_START → ORIENT          (automatic)
ORIENT        → INTAKE          (after exit criteria met)
INTAKE        → PLAN            (after triage)
INTAKE        → ORIENT          (loop: re-check state)
PLAN          → EXECUTE         (after plan approved)
EXECUTE       → UPDATE          (after work done)
EXECUTE       → PLAN            (loop: re-plan if scope changes)
UPDATE        → SESSION_END     (after docs updated)
UPDATE        → INTAKE          (loop: more work discovered)
```

### 6.3 Hook Gates

| Hook Event | Matcher | Gate | Behavior |
|-----------|---------|------|----------|
| SessionStart | * | — | Initialize ORIENT, show KPIs |
| PreToolUse | Edit\|Write | EXECUTE | **Block** unless EXECUTE or UPDATE |
| PreToolUse | EnterPlanMode | PLAN | **Block** unless INTAKE or EXECUTE |
| PostToolUse | ExitPlanMode | — | Auto-transition to EXECUTE |
| Stop | * | SESSION_END | **Warn** (not block) if not in UPDATE/SESSION_END |

### 6.4 Hook JSON Configuration

The exact JSON merged into `.claude/settings.json` by `devlead init`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [{
          "type": "command",
          "command": "devlead start",
          "timeout": 15,
          "statusMessage": "Initializing DevLead session..."
        }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "devlead gate EXECUTE",
          "timeout": 5,
          "statusMessage": "Checking state gate..."
        }]
      },
      {
        "matcher": "EnterPlanMode",
        "hooks": [{
          "type": "command",
          "command": "devlead gate PLAN",
          "timeout": 5,
          "statusMessage": "Checking plan gate..."
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [{
          "type": "command",
          "command": "devlead transition EXECUTE",
          "timeout": 5,
          "statusMessage": "Transitioning to EXECUTE..."
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "devlead gate SESSION_END",
          "timeout": 10,
          "statusMessage": "Checking session end..."
        }]
      }
    ]
  }
}
```

**Note:** `EnterPlanMode` and `ExitPlanMode` are confirmed Claude Code tool names, matchable by `PreToolUse`/`PostToolUse` hooks. Verified in production (eTrading project, April 2026).

### 6.5 Error Handling

| Scenario | Behavior |
|----------|----------|
| `session_state.json` missing | `gate` commands block with "SESSION NOT INITIALIZED" message. `start` creates fresh state. |
| `session_state.json` corrupted | `start` overwrites with fresh state. Other commands block with parse error. |
| Required markdown file missing | KPIs return 0 for that metric. `doctor` reports the missing file. No crash. |
| Invalid state in file | `gate` and `transition` report error, suggest `devlead start` to reset. |
| Hook timeout (>5s) | Claude Code treats as non-blocking error. Session continues without gate enforcement. |

**Principle:** DevLead degrades gracefully. A broken state file never prevents work — it warns and resets. The `doctor` command diagnoses installation health.

### 6.7 Exit Criteria Checklists (Complete)

| State | Key | Description |
|-------|-----|-------------|
| ORIENT | `status_read` | Read `_project_status.md` |
| ORIENT | `tasks_read` | Read `_project_tasks.md` |
| ORIENT | `intake_scanned` | Scanned all `_intake_*.md` files |
| ORIENT | `kpis_reported` | Reported KPI dashboard to user |
| INTAKE | `requests_captured` | All user requests registered in `_intake` files |
| INTAKE | `triaged` | New items triaged into `_project_tasks.md` |
| UPDATE | `intake_updated` | Closed resolved `_intake` items |
| UPDATE | `tasks_updated` | Updated `_project_tasks.md` (mark done, add new) |
| UPDATE | `status_updated` | Updated `_project_status.md` with session results |
| UPDATE | `living_reviewed` | Updated `_living` docs if architecture changed |
| UPDATE | `memory_derived` | `MEMORY.md` regenerated from `claude_docs/` |

**PLAN and EXECUTE have no checklists.** PLAN exits automatically when `ExitPlanMode` fires (hook-driven). EXECUTE exits when the user triggers transition to UPDATE (judgment call, not checklist).

### 6.8 State Persistence

```json
// claude_docs/session_state.json (gitignored)
{
    "state": "ORIENT",
    "session_start": "2026-04-05T10:30:00",
    "transitions": [
        {"from": "SESSION_START", "to": "ORIENT", "at": "2026-04-05T10:30:01"}
    ],
    "checklists": {
        "ORIENT": {
            "status_read": false,
            "tasks_read": false,
            "intake_scanned": false,
            "kpis_reported": false
        },
        "INTAKE": {
            "requests_captured": false,
            "triaged": false
        },
        "UPDATE": {
            "intake_updated": false,
            "tasks_updated": false,
            "status_updated": false,
            "living_reviewed": false,
            "memory_derived": false
        }
    }
}
```

## 7. Document Model

### 7.1 Four File Types

| Type | Naming | Location | Purpose |
|------|--------|----------|---------|
| User Profile | `~/.claude/user_info.md` | Outside repo | Personal preferences (only non-repo file) |
| Living | `_living_*.md` | `claude_docs/` | Evergreen reference — architecture, standards, guides |
| Intake | `_intake_*.md` | `claude_docs/` | Incoming requests — bugs, features, gaps, changes |
| Project | `_project_*.md` | `claude_docs/` | Work plan — status, tasks, roadmap |

### 7.2 Data Flow

```
_intake docs (requests arrive)
    → _project_roadmap (stories/epics)
    → _project_tasks (actionable work items)
    → EXECUTE (code changes)
    → _project_status (session results)
    → _living docs (architecture updates)
    → ~/.claude/memory/MEMORY.md (derived thin index)
```

### 7.3 Memory Derivation

`~/.claude/memory/MEMORY.md` is **derived from** `claude_docs/`. It stays at Claude's conventional location but contains only an index pointing to `claude_docs/` files. Never the reverse.

### 7.4 Monthly Rollover

Files that grow fast are archived monthly:

```
claude_docs/archive/
├── _project_tasks_2026-03.md     # Immutable snapshot
├── _project_tasks_2026-04.md
├── _intake_bugs_2026-03.md
└── ...
```

Open items carry forward. Closed items stay in archive only.

## 8. KPI Engine

### 8.1 Architecture

```
┌─────────────────────────────────────────────────┐
│ KPI Engine                                       │
│                                                  │
│  ┌──────────────┐    ┌────────────────────────┐ │
│  │ Doc Parser    │───▶│ Built-in Variables      │ │
│  │ (reads md)    │    │ (counts from docs)      │ │
│  └──────────────┘    └───────────┬────────────┘ │
│                                   │              │
│                    ┌──────────────▼───────────┐  │
│                    │ Formula Evaluator         │  │
│                    │ (computes KPI scores)     │  │
│                    └──────────────┬───────────┘  │
│                                   │              │
│         ┌─────────────────────────┼──────────┐  │
│         │                         │          │  │
│  ┌──────▼──────┐  ┌──────────────▼───┐ ┌────▼─┐│
│  │ Built-in     │  │ Custom (TOML)    │ │Plugin││
│  │ KPIs         │  │ KPIs             │ │(.py) ││
│  └─────────────┘  └─────────────────┘ └──────┘│
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ Dashboard Renderer (terminal output)      │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

DevLead computes all KPIs. Projects define what to compute. Three tiers:

| Tier | How Defined | For |
|------|------------|-----|
| **Built-in KPIs** | Hardcoded in DevLead | Universal governance metrics — work for every project |
| **Custom TOML KPIs** | `devlead.toml` formulas | Project-specific metrics using built-in variables |
| **Plugin KPIs** | Python file in project | Complex domain logic that can't be expressed as a formula |

### 8.2 Built-in KPIs (23 KPIs, Ship With DevLead)

All built-in KPIs are universal — they work for any project using DevLead. No configuration required.

#### Category A: LLM Effectiveness (Is the AI getting better?)

| # | KPI | What It Catches | Signal | Range |
|---|-----|----------------|--------|-------|
| 1 | **LLM Learning Curve** | Is the LLM improving over time? | Trend of gate violations, circles, FTR, plan revisions across sessions. Rolling 5-session avg vs 10-session avg. | 0-100 (100 = improving) |
| 2 | **Going in Circles** | Repetitive unproductive work | EXECUTE→PLAN loops (+20), same file edited 3x (+15), reopens (+30), plan revisions after execution (+25) | 0-100 (lower = better) |
| 3 | **Skin in the Game** | Acting without understanding what it's solving | Skipped ORIENT/INTAKE before EXECUTE, plan has no story/objective reference | 0-100 (higher = better) |
| 4 | **Definition of Done** | Premature "done" claims | Tasks marked DONE that get REOPENED, UPDATE exit criteria skipped | 0-100 (higher = better) |
| 5 | **Plan Adherence** | Going rogue from approved plan | Files edited not in plan, tasks completed not in plan, scope additions | 0-100 (higher = better) |
| 6 | **State Discipline** | Bypassing the state machine | Gate violation attempts per session (hook blocks counted) | 0-100 (higher = fewer violations) |
| 7 | **Session Completeness** | Leaving without cleanup | Sessions ending without reaching UPDATE, docs not refreshed | 0-100 (higher = better) |
| 8 | **First-Time-Right** | Rework needed on "completed" work | Tasks that stayed DONE / total ever marked DONE | 0-100% |
| 9 | **Bug Introduction Rate** | Creating bugs while building features | New `_intake_bugs` items filed during EXECUTE state | Count (lower = better) |
| 10 | **Scope Creep** | Work expanding beyond approved plan | Tasks added during EXECUTE not in original plan | Count (lower = better) |

Requires `claude_docs/session_history.jsonl` — one line appended per completed session:
```jsonl
{"date":"2026-04-05","circles":12,"ftr":78,"gate_violations":2,"plan_revisions":1,"session_complete":true,"dod_score":85,"bugs_introduced":1}
```

#### Category B: Delivery & Project Management (Is business value being produced?)

| # | KPI | What It Catches | Signal | Range |
|---|-----|----------------|--------|-------|
| 11 | **Code-Domain Convergence** | Writing code that doesn't deliver business objectives | Tasks without story refs / total active tasks. Recommendations always state which objective is advanced. | 0-100 (higher = better) |
| 12 | **Roadmap Velocity** | Stories not closing | Stories completed this session / average stories per session | 0-100 (higher = better) |
| 13 | **Intake Throughput** | Backlog growing, not shrinking | intake_closed / intake_total. Trending ratio. | 0-100% |
| 14 | **Blocker Resolution** | Blocked items rotting | Average days items stay BLOCKED before resolution | Days (lower = better) |
| 15 | **Value per Session** | Sessions that produce no deliverable | Stories or tasks completed this session. 0 = wasted session. | Count |
| 16 | **Bug-to-Feature Ratio** | More bugs than features shipping | intake_bugs_open / tasks_done | Ratio (lower = better) |
| 17 | **Risk Concentration** | Too much work in one area | Tasks clustered on same epic. Herfindahl index of task-to-epic distribution. | 0-100 (lower = balanced) |
| 18 | **Next Best Action** | What to work on and WHY | Highest priority unblocked task + which business objective it advances | Text recommendation |

#### Category C: Project Health (Is the system of record healthy?)

| # | KPI | What It Catches | Signal | Range |
|---|-----|----------------|--------|-------|
| 19 | **Doc Freshness** | Stale docs = stale understanding | Days since `_project_status.md` and `_living_*` docs updated | 0-100 (higher = fresher) |
| 20 | **Traceability** | Orphan work with no tracking | Tasks without story ref + stories without intake origin | 0-100 (higher = traced) |
| 21 | **Intake Staleness** | Requests rotting in backlog | Items open >7 days without action | Count (lower = better) |
| 22 | **Archive Health** | Monthly rollover not happening | Months since last rollover, file sizes growing | 0-100 |
| 23 | **Coverage Gap** | Missing doc types | Expected files that don't exist (no roadmap, no intake, etc.) | Count (0 = healthy) |

### 8.3 Built-in Variables (Available to All KPIs)

The doc parser reads `claude_docs/` files and produces these variables:

| Variable | Source | Description |
|----------|--------|-------------|
| `tasks_open` | `_project_tasks.md` | Tasks with status OPEN |
| `tasks_in_progress` | `_project_tasks.md` | Tasks with status IN_PROGRESS |
| `tasks_done` | `_project_tasks.md` | Tasks with status DONE or COMPLETE |
| `tasks_total` | `_project_tasks.md` | All tasks (open + in progress + done) |
| `tasks_blocked` | `_project_tasks.md` | Tasks with status BLOCKED |
| `tasks_reopened` | `_project_tasks.md` | Tasks with status containing REOPEN |
| `tasks_overdue` | `_project_tasks.md` | Tasks where Due date < today |
| `tasks_with_story` | `_project_tasks.md` | Tasks with Story column matching `S-NNN` or `E-NNN` |
| `tasks_active` | `_project_tasks.md` | Open + in progress (not done, not closed) |
| `stories_total` | `_project_roadmap.md` | Total stories/epics |
| `stories_done` | `_project_roadmap.md` | Stories marked DONE or with `[x]` checkbox |
| `intake_open` | `_intake_*.md` | Open intake items across all files |
| `intake_closed` | `_intake_*.md` | Closed intake items across all files |
| `intake_total` | `_intake_*.md` | All intake items |
| `intake_bugs_open` | `_intake_bugs.md` | Open bugs specifically |
| `intake_features_open` | `_intake_features.md` | Open features specifically |
| `intake_gaps_open` | `_intake_gaps.md` | Open gaps specifically |
| `convergence` | Computed | `stories_done / stories_total * 100` (built-in KPI result) |

**Detection rules:**

| Term | How Detected |
|------|-------------|
| Status = OPEN | Column text contains "OPEN" (case-insensitive) |
| Status = DONE | Column text contains "DONE" or "COMPLETE" |
| Status = REOPEN | Column text contains "REOPEN" |
| Status = BLOCKED | Column text contains "BLOCKED" |
| Story reference | Column text matches regex `S-\d+` or `E-\d+` |
| Overdue | Due column parsed as YYYY-MM-DD, compared to today |
| Checkbox done | Line matches `- [x]` (case-insensitive) |

**Task table expected format** (parsed by `doc_parser.py`):

```markdown
| ID | Task | Story | Priority | Status | Assignee | Due | Blockers |
```

DevLead parses by column header name, not position. If a column is missing, that variable returns 0. The `doctor` command warns about missing columns.

### 8.4 Custom KPIs via TOML (No Code Required)

Define project-specific KPIs using built-in variables and arithmetic:

```toml
# devlead.toml

[[kpis.custom]]
name = "Skin in the Game"
description = "Is work aligned with business objectives?"
formula = "(tasks_with_story / tasks_active) * 40 + (convergence / 100) * 40 + (intake_closed / intake_total) * 20"
range = [0, 100]
warning_below = 50
format = "score"       # "score" (0-100), "percent", "count", "ratio"

[[kpis.custom]]
name = "Go-Live US"
description = "US market launch readiness"
formula = "stories_done / stories_total * 100"
range = [0, 100]
warning_below = 80
format = "percent"

[[kpis.custom]]
name = "Blocked Ratio"
description = "How much work is stuck"
formula = "tasks_blocked / tasks_active * 100"
range = [0, 100]
warning_above = 30
format = "percent"

[[kpis.custom]]
name = "Bug Debt"
description = "Unfixed bugs relative to features delivered"
formula = "intake_bugs_open / tasks_done * 100"
range = [0, 100]
warning_above = 25
format = "percent"
```

**Formula language:**
- Variables: any built-in variable from section 8.3
- Operators: `+`, `-`, `*`, `/`
- Parentheses for grouping
- Division by zero returns 0 (safe default)
- Result clamped to `range` if specified

**No `eval()`.** The formula evaluator is a safe expression parser — whitelist of variable names and arithmetic operators only. No function calls, no imports, no arbitrary code execution.

### 8.5 Plugin KPIs via Python (For Complex Logic)

When a formula can't express the logic (e.g., reading external APIs, complex conditional logic, cross-referencing multiple files):

```toml
[[kpis.plugin]]
name = "Trading Desk Coverage"
description = "How many trading desks have active positions"
module = "kpis/desk_coverage.py"
```

The Python file must implement a single function:

```python
# kpis/desk_coverage.py
from devlead.kpi_engine import KpiResult, BuiltinVars

def compute(vars: BuiltinVars, docs_dir: Path) -> KpiResult:
    """Custom KPI — can read any file, do any logic."""
    # Read project-specific files
    roadmap = (docs_dir / "_project_roadmap.md").read_text()
    
    # Custom logic here
    desks_with_positions = count_active_desks(roadmap)
    total_desks = 6
    
    return KpiResult(
        value=desks_with_positions / total_desks * 100,
        format="percent",
        detail=f"{desks_with_positions}/{total_desks} desks active",
        warning=desks_with_positions < 3,
    )
```

**Plugin contract:**
- File must have a `compute(vars, docs_dir)` function
- Receives built-in variables + path to `claude_docs/`
- Returns a `KpiResult` (value, format, detail, warning flag)
- Must not have side effects (read-only)
- Timeout: 5 seconds per plugin (kills slow plugins)

### 8.6 KPI Dashboard Output

```
========================================================================
  DevLead — 2026-04-05
========================================================================

  A. LLM EFFECTIVENESS
  ----------------------------------------------------------------
  Learning Curve    | 72/100 (IMPROVING) | 5-session trend: +8
  Going in Circles  | 12/100 (OK)       | 0 loops, 1 reopen
  Skin in the Game  | 85/100 (STRONG)   | Plan refs story S-003
  Definition of Done| 78/100            | 2/23 reopened
  Plan Adherence    | 90/100            | 1 unplanned file edit
  State Discipline  | 95/100            | 1 gate violation
  Session Complete  | 100/100           | UPDATE reached
  First-Time-Right  | 91%               | 21/23 stayed done
  Bugs Introduced   | 1 this session    | OK
  Scope Creep       | 0 unplanned tasks | Clean execution

  B. DELIVERY & PROJECT MANAGEMENT
  ----------------------------------------------------------------
  Code-Domain Conv. | 80/100            | 16/20 tasks have story ref
  Roadmap Velocity  | 2 stories/session | Above average
  Intake Throughput | 65%               | 13/20 closed
  Blocker Resolve   | 2.1 days avg      | OK
  Value per Session | 3 tasks           | Productive
  Bug:Feature Ratio | 0.15              | Healthy
  Risk Concentration| 35/100 (balanced) | Work spread across 4 epics
  >> Next Best Action: TASK-045 — Broker connection test
     Advances: E-003 (Go-Live US) — 3/12 → 4/12

  C. PROJECT HEALTH
  ----------------------------------------------------------------
  Doc Freshness     | 95/100            | Status: today, Living: 2d ago
  Traceability      | 80/100            | 4 orphan tasks
  Intake Staleness  | 2 items > 7 days  | !! Needs attention
  Archive Health    | OK                | Last rollover: 2026-04-01
  Coverage Gap      | 0 missing files   | All docs present

  CUSTOM (project-specific KPIs from devlead.toml)
  ----------------------------------------------------------------
  Go-Live US        | 25%               | 3/12 checks
  Desk Coverage     | 67%               | 4/6 desks active

  State: ORIENT | Next: INTAKE
  Pipeline: 8 open | 2 in progress | 18 done
========================================================================
```

3 built-in categories (A/B/C) + custom section. Warnings marked with `!!`. Next Best Action always states which business objective is advanced.

### 8.7 Configurable Thresholds

```toml
[kpis]
# Built-in KPI thresholds
circles_warning = 50        # Going in Circles > this = WARNING
ftr_minimum = 60            # First-Time-Right < this = WARNING
convergence_target = 80     # Target convergence %

# Custom KPI thresholds are per-KPI (see 8.4)
```

## 9. CLI

### 9.1 Commands

```bash
devlead init                     # Scaffold claude_docs/, configure hooks
devlead status                   # Current state + KPIs
devlead transition <STATE>       # Advance state (validates exit criteria)
devlead gate <REQUIRED>          # Hook gate check (exit 0 or 2)
devlead checklist <state> <key>  # Mark exit criterion done
devlead kpis                     # Full KPI dashboard
devlead rollover                 # Monthly archive
devlead start                    # SessionStart hook handler
devlead doctor                   # Verify installation health
```

### 9.2 Init Behavior

1. Creates `claude_docs/` with template files from `scaffold/`
2. Creates `devlead.toml` with defaults
3. Merges hook config into `.claude/settings.json` (preserves existing hooks)
4. Adds `claude_docs/session_state.json` to `.gitignore`

If files exist: warn, offer merge/skip/overwrite per file.

### 9.3 Doctor Command

```bash
$ devlead doctor

  DevLead Health Check
  [OK] claude_docs/ exists
  [OK] devlead.toml found
  [OK] .claude/settings.json has hooks configured
  [OK] session_state.json is gitignored
  [OK] _project_status.md exists
  [OK] _project_tasks.md exists
  [OK] _project_roadmap.md exists
  [WARN] _intake_bugs.md is empty — no items tracked yet
  [OK] All gates functional
```

## 10. Configuration

### 10.1 devlead.toml

```toml
[project]
name = "my-project"
docs_dir = "claude_docs"           # Override if needed

[states]
# Future: allow custom state names/order

[kpis]
circles_warning = 50
ftr_minimum = 60
convergence_target = 80

[rollover]
day_of_month = 1
retain_months = 12
files = [
    "_project_tasks.md",
    "_intake_bugs.md",
    "_intake_features.md",
    "_intake_gaps.md",
    "_intake_changes.md",
]

[hooks]
session_start = true
gate_edits = true
gate_plan_mode = true
gate_session_end = true
```

## 11. Testing Strategy

### 11.1 Unit Tests

| Module | What's Tested |
|--------|-------------|
| `test_state_machine.py` | Valid/invalid transitions, gate allow/block, exit criteria enforcement |
| `test_kpi_engine.py` | KPI computation with fixture docs (known task counts → known scores) |
| `test_doc_parser.py` | Markdown table parsing, item counting, status detection |
| `test_rollover.py` | Archive creation, open item carry-forward, closed item removal |
| `test_cli.py` | CLI command dispatch, init scaffolding, hook config merging |

### 11.2 Integration Tests

- `devlead init` in a temp directory → verify all files created
- Full state flow: start → orient → intake → plan → execute → update → end
- Hook simulation: call `devlead gate` with different states, verify exit codes

### 11.3 Test Fixtures

Sample markdown files in `tests/fixtures/` with known data for deterministic KPI testing.

## 12. Multi-Project Portfolio (Pro Tier)

### 12.1 Architecture

```
~/.devlead/                              # DevLead home (user-level)
├── workspace.toml                       # Registered projects
├── portfolio_history.jsonl              # Aggregate KPI history across projects
│
│   Per-project (unchanged from single-project):
├── ~/projects/eTrading/claude_docs/     # Project A
├── ~/projects/income_desk/claude_docs/  # Project B
└── ~/projects/devlead/claude_docs/      # Project C
```

### 12.2 Workspace Registration

```bash
devlead portfolio add ~/projects/eTrading --name "eTrading"
devlead portfolio add ~/projects/income_desk --name "income_desk"
devlead portfolio list
devlead portfolio remove eTrading
```

```toml
# ~/.devlead/workspace.toml
[[projects]]
name = "eTrading"
path = "C:/Users/nitin/PythonProjects/eTrading"

[[projects]]
name = "income_desk"
path = "C:/Users/nitin/PythonProjects/income_desk"
```

### 12.3 Portfolio Dashboard

```bash
devlead portfolio
```

```
========================================================================
  DevLead Portfolio — 2026-04-05
========================================================================

  PROJECT          | Convergence | Circles | FTR  | LLM Learning | State
  -----------------------------------------------------------------------
  eTrading         | 35%         | 12/100  | 78%  | IMPROVING     | EXECUTE
  income_desk      | 62%         | 5/100   | 91%  | STABLE        | ORIENT

  CROSS-PROJECT
  -----------------------------------------------------------------------
  Portfolio Conv.  | 48% (weighted)
  Total velocity   | 4 stories/day across 2 projects
  Biggest blocker  | GAP-006 in eTrading blocks FEAT-002 in income_desk
  Time allocation  | eTrading 70% | income_desk 30%
  Weakest link     | eTrading (convergence declining -5% this week)

  >> Next Best Action (cross-project):
     1. income_desk: Close REQUEST-003 (unblocks eTrading TASK-045)
        Advances: eTrading Go-Live US 3/12 → 4/12
     2. eTrading: TASK-048 — Exit monitor integration
        Advances: eTrading Go-Live US 4/12 → 5/12
========================================================================
```

### 12.4 Cross-Project Collaboration Channel

Projects that depend on each other need a communication channel. DevLead provides this via a `.collab/` folder convention — a shared mailbox between projects.

**How it works:**

Each project has a `.collab/` folder at its root. When Project A needs something from Project B, it writes a request file. When Project B's DevLead session starts (ORIENT state), it scans for incoming requests and registers them as `_intake` items.

```
eTrading/.collab/
├── OUTBOX/                          # Requests FROM eTrading TO other projects
│   └── REQUEST_income_desk_001.md   # "We need batch_reprice to support X"
└── INBOX/                           # Requests FROM other projects TO eTrading
    └── FEEDBACK_income_desk_003.md  # "Here's why batch_reprice works this way"

income_desk/.collab/
├── OUTBOX/
│   └── FEEDBACK_etrading_003.md     # Response to eTrading's request
└── INBOX/
    └── REQUEST_etrading_001.md      # eTrading's request lands here
```

**Collab file format:**

```markdown
# REQUEST: Batch reprice support for multi-leg trades

> From: eTrading
> To: income_desk
> Date: 2026-04-05
> Priority: P1
> Blocks: eTrading/TASK-045
> Status: OPEN

## What We Need
batch_reprice() currently only handles single-leg trades...

## Why It Matters
This blocks Go-Live US gate 4/12...

## Acceptance Criteria
- [ ] batch_reprice handles multi-leg TradeSpecs
- [ ] Returns per-leg Greeks
```

**DevLead automation:**

| When | What DevLead Does |
|------|------------------|
| `devlead init` | Creates `.collab/INBOX/` and `.collab/OUTBOX/` |
| ORIENT state | Scans `.collab/INBOX/` for new requests → registers as `_intake_changes.md` items |
| EXECUTE state | If work resolves a collab request → writes response to `.collab/OUTBOX/` |
| `devlead portfolio` | Shows cross-project blockers from collab channel |
| Portfolio KPIs | Counts open collab requests as cross-project blockers |

**Sync mechanism:**

For projects on the same machine (like eTrading + income_desk), DevLead can symlink or copy between `.collab/` folders:

```bash
devlead collab sync   # Push OUTBOX to target project's INBOX
```

For remote projects (different machines/repos), `.collab/` is committed to git. PR-based collaboration.

### 12.5 Cross-Project KPIs

| # | KPI | What It Measures | Signal |
|---|-----|-----------------|--------|
| 24 | **Portfolio Convergence** | Weighted avg convergence across projects | Per-project convergence × project weight |
| 25 | **Cross-Project Blockers** | Dependencies between projects that are stuck | Open collab requests with Status: OPEN |
| 26 | **Time Allocation Balance** | Is one project starving? | Sessions per project over rolling 7 days |
| 27 | **Weakest Link** | Which project needs attention most? | Project with worst composite KPI score |
| 28 | **Portfolio Velocity** | Aggregate delivery rate | Total stories completed across all projects per week |
| 29 | **Context Switch Cost** | Jumping between projects too often? | Project switches per day (high = fragmented attention) |
| 30 | **Collab Response Time** | Are cross-project requests getting answered? | Avg days from REQUEST filed to FEEDBACK received |

### 12.6 CLI Commands (Pro)

```bash
devlead portfolio                        # Cross-project dashboard
devlead portfolio add <path> --name <n>  # Register project
devlead portfolio remove <name>          # Unregister
devlead portfolio sync                   # Refresh all project KPIs
devlead collab sync                      # Push outbox to target inboxes
devlead collab status                    # Show open cross-project requests
devlead next --all                       # Next best action across ALL projects
devlead kpis --all                       # KPIs for every project
devlead status --project <name>          # Single project status
```

---

## 13. What DevLead Does NOT Do

- **Does not ship code.** It governs the development phase, not deployment or release.
- **Does not replace PM tools.** No Jira, no Linear, no sprint ceremonies. DevLead governs how AI assists in development — it doesn't manage your project backlog.
- **Does not write code.** It governs the AI that writes code. The development, not the developer.
- **Does not dictate doc content.** It enforces doc types and flow. What you write in those docs is your business.
- **Does not require a server.** Pure CLI, runs locally.
- **Does not phone home.** No telemetry, no license server.
- **Does not lock you in.** If you uninstall, your `claude_docs/` files still work as plain markdown.

## 14. Future

- Node.js adapter for npm distribution
- Cursor/Copilot hook adapters
- Team analytics (aggregate KPIs across projects)
- Plugin system for custom states/gates
- Web dashboard for KPI visualization
- CI/CD integration (fail build if KPIs below threshold)
