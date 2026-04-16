# DevLead User Guide

DevLead is a governance layer that installs onto any project using Claude Code and
makes `devlead_docs/` the **single source of truth** for what gets built, what got
built, and why. It does not replace Claude Code or any other plugin - it sits
alongside them and enforces traceability.

## Core idea in one sentence

If a line of code cannot be traced back to a scratchpad note or an intake entry,
it is **dark code** - and DevLead either prevents it or flags it.

---

## What DevLead changes about Claude's behavior

DevLead is not a background service. It shapes the model's behavior through three
concrete channels:

### 1. Where Claude looks for context (session start)

Every session, Claude reads files in a fixed order before anything else:

1. `devlead_docs/_resume.md` - session memory: locked decisions, open threads,
   "where we are, what's next".
2. `devlead_docs/_scratchpad.md` - raw untriaged capture from prior sessions.
3. Files referenced in `_resume.md` Section 14 (the next-action cursor).

This is enforced by a rule in `CLAUDE.md`. Effect: no matter how long you have
been away, Claude re-grounds itself in the canonical store first, not in partial
LLM memory.

### 2. Where work originates (capture -> triage -> plugin flow -> intake)

Any idea, bug, or feature you mention gets captured **verbatim** to
`_scratchpad.md` - no summarization, no interpretation, no loss. The scratchpad
is an inbox, not a backlog.

When an entry is ready to become real work, you (or Claude) run `/devlead triage`.
Triage is a short interactive walk: for each scratchpad entry, decide whether to
leave it, plan it, or migrate it to a dedicated file.

The plan-and-ingest path is where the bridge earns its keep. Claude runs your
project's **normal** planning flow - whatever plugins are installed. With
superpowers installed, that is `brainstorming -> writing-plans`. Nothing is
changed about how those plugins work. When they finish, Claude calls
`/devlead ingest <plan-path> --type features|bug_issues` and the plan is filed
into `devlead_docs/_intake_features.md` or `_intake_bug_issues.md` as a new
entry with a tracking ID (INTF-NNNN or INTB-NNNN) and a pointer back to the
source plugin output.

From intake, entries get promoted to the BO/TBO/TTO hierarchy in
`_project_hierarchy.md`. Once an entry is promoted, any code written against it
is trivially traceable back to its origin.

### 3. Where work ends up (canonical store, always)

Every outcome - design docs, code changes, decisions, commitments - lives in
`devlead_docs/` or traces back to a file there. LLM memory is a derived cache;
if you lose it, you rebuild from disk. Other plugins keep writing to their own
native locations (`docs/superpowers/specs/`, etc.) - DevLead never touches them.

---

## Architecture (top to bottom)

1. **User** - the human engineer.
2. **Capture layer** - `_scratchpad.md` + the `/devlead scratchpad` command.
   Raw notes in, nothing interpreted.
3. **Store layer** - the files in `devlead_docs/`. Canonical source of truth.
   Permanent. Markdown for human-readable state, JSONL for append-only logs.
4. **Bridge layer** - `src/devlead/scratchpad.py`, `intake.py`, `bridge.py`,
   slash commands in `commands/`. Moves plugin outputs into the store without
   modifying the plugins. Claude-driven.
5. **Hierarchy** - `Vision -> Goals -> Phase -> BO -> TBO -> TTO` in
   `_project_hierarchy.md`. BO = Business Objective. TBO = Tangible Business
   Outcome ("user can now do X"). TTO = Tangible Technical Objective (the
   atomic work unit). Siblings carry weights summing to 100 so progress rolls
   up mathematically.
6. **Governance layer** *(designed, not built yet)* - hooks that fire on
   `SessionStart`, `UserPromptSubmit`, `PreToolUse(Edit|Write)`, and `Stop`.
   Each hook runs `devlead gate <event>` which evaluates rules from
   `devlead.toml` and either logs (warn mode) or blocks (strict mode). Default
   is warn-only; nothing exits non-zero unless strict mode is explicitly on.
7. **Convergence engine** *(designed, not built)* - the rollup math that turns
   leaf TTO progress into BO and Phase convergence scores. Drives the K1
   Convergence KPI.
8. **Visibility layer** *(designed, partially scaffolded)* - `/devlead status`
   text output in v1, HTML dashboard in v1.1. Shows convergence, KPIs,
   project maturity score, scratchpad burndown.
9. **Audit layer** *(skeleton in place)* - `_audit_log.jsonl` and
   `_promise_ledger.jsonl` exist but are empty. Every gate decision, migration,
   and commitment will write here.

---

## What's built today (Session 3, 2026-04-14)

- `devlead init` - scaffolds 18 files into `devlead_docs/` on any project,
  idempotently.
- `_scratchpad.md`, `_resume.md` - raw capture + session memory, both first-class.
- `_intake_features.md`, `_intake_bug_issues.md` - intake files with a locked
  schema (INTF-/INTB- IDs, source traceability, actionable-items list).
- `_living_decisions.md` - append-only log of locked decisions.
- `/devlead scratchpad`, `/devlead intake`, `/devlead triage`, `/devlead ingest` -
  the four bridge commands.
- Session-start rule in `CLAUDE.md` so Claude reads `_resume.md` and
  `_scratchpad.md` first every time.

If DevLead were uninstalled right now, nothing else would change - no plugin is
modified, no hook is registered, no file outside `devlead_docs/` is touched.

## What's designed but not built

| Feature | Status | Landing target |
|---|---|---|
| Store layer parsers (BO/TBO/TTO read/write) | Designed | Day 4-5 |
| Hook infrastructure (4 hooks registered) | Designed | Day 5-6 |
| Gate engine (warn/block + rules DSL) | Designed | Day 6 |
| Convergence math + K1 KPI | Designed | Week 2 |
| K5 Tokenomics, K7 Drift, K8 Goal Yield, K9 Word-Keeping | Designed | Week 2 |
| Goals + commitments (/goal, /commit, /resolve) | Designed | Week 2 |
| Promise Ledger | Designed | Week 2 |
| `/devlead status` text + HTML dashboard | Designed | Week 2 / v1.1 |
| `/devlead pivot` repivot ceremony | Designed | Week 3 |
| Dark-code detection (enforcement) | Principle locked, mechanism deferred | v1.1 |
| Licensing + paid tier + marketplace | Designed | Week 4 |
| `/devlead interview` as own command | **Replaced** - plugin bridge subsumes it | n/a |

---

## What's configurable without coding

**Today: nothing.** All defaults live in code. The `devlead.toml` file from v1
was archived and has not been rebuilt yet.

**Designed: two layers.**

### Layer 1 - `.claude/settings.json` (DevLead-owned plumbing)

Written automatically by `/devlead init` once hook infrastructure ships. Routes
each Claude Code hook event to a `devlead gate <event>` call. Users do not edit
this file manually.

### Layer 2 - `devlead.toml` at project root (user-owned)

Plain TOML. Designed sections:

- `[enforcement]` - global mode: `"warn"` (default) or `"block"` (strict)
- `[[enforcement.rules]]` - per-rule: event, matcher, check, action, message
- `[kpis]` - thresholds (e.g. `drift_warn = 0.5`)
- `[interview]` - block order, lock requirements (if/when interview returns)
- `[goals]` - at-risk window (default 20% of target date), convergence threshold
- `[bridge]` - plugin adapters (spec/plan path patterns, default intake type
  per source)

Changing `enforcement.mode = "block"` flips the gate engine from warn-only to
strict in a single edit. Users who want maximum constraint get it for free;
users who want minimal friction stay in warn mode forever.

---

## File map inside `devlead_docs/`

| File | Role |
|---|---|
| `_resume.md` | Session memory: locked decisions, open threads, where-we-are |
| `_scratchpad.md` | Raw untriaged capture |
| `_project_status.md` | Flags derived from other files (no state machine) |
| `_project_hierarchy.md` | BO / TBO / TTO tree with weights |
| `_intake_features.md` | Feature intake entries (INTF-NNNN) |
| `_intake_bug_issues.md` | Bug/issue intake entries (INTB-NNNN) |
| `_living_project.md` | What the project IS |
| `_living_goals.md` | First-class goals with target dates |
| `_living_metrics.md` | Project-specific metrics |
| `_living_technical.md` | Tech stack, architecture notes |
| `_living_design.md` | How the system is shaped |
| `_living_decisions.md` | Append-only log of locked decisions |
| `_living_glossary.md` | Project-specific vocabulary |
| `_living_standing_instructions.md` | Rules that persist across sessions |
| `_living_risks.md` | Known risks and mitigations |
| `_audit_log.jsonl` | Every gate event and migration (append-only) |
| `_promise_ledger.jsonl` | Every commitment Claude makes (append-only) |
| `interview_template.md` | The 5-block interview playbook (reference copy) |

---

## Command quick reference (built today)

| Command | What it does |
|---|---|
| `/devlead init [path]` | Scaffold `devlead_docs/` (18 files, idempotent) |
| `/devlead scratchpad [path]` | List raw-capture entries |
| `/devlead intake [--type TYPE]` | List intake entries by type |
| `/devlead triage` | Walk scratchpad entries interactively |
| `/devlead ingest <plan> --type TYPE` | File a plugin plan into an intake |

For the plugin-bridge flow in detail, see `docs/plugin-bridge.md`.
