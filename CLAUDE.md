# CLAUDE.md — DevLead v2

## What this project is

DevLead is a governance tool that installs onto an existing project and becomes the **only** channel between the codebase and the model. v2 is under construction — the product is being dictated section by section by the user.

## Session rules — read every time

1. **`devlead_docs/` is the single, canonical source of truth.** Both ways. What needs to be done comes from here. What got done gets written back here. There is no other system of record.
2. **LLM memory is a derived view of `devlead_docs/`.** Memory can hold content, but every piece of that content originated in `devlead_docs/`. Memory is a cache, never an independent source.
3. **No jumping the gun.** The model cannot edit code, plan, or discuss work that did not originate in `devlead_docs/`. Both file edits AND conversation planning are covered.
4. **Mandatory ordering:** scratchpad → triage → plugin plan → intake → hierarchy → coding → write-back. Coding only begins *after* the work has been materialized into a TTO under `_project_hierarchy.md`.
5. **Work originates two ways:** user + Claude defining it together, OR Claude identifying and creating the work item itself.

## Session start — read order (hard rule)

At the start of every session, read files in this order before anything else:

1. `devlead_docs/_resume.md` — thin bootstrap cursor: what to read, the next action, any open blockers. ~30-50 lines max.
2. `devlead_docs/_intake_*.md` — look for entries with `status: in_progress`. Those are the current focus (what Claude was actively working on). Run `/devlead focus show` to list them.
3. `devlead_docs/_aware_features.md` and `devlead_docs/_aware_design.md` — self-awareness files describing the current state of the code (auto-derived). `_aware_*` is its own category, distinct from `_living_*`, and will keep evolving.
4. `devlead_docs/_scratchpad.md` — raw untriaged capture from prior sessions.
5. `devlead_docs/_living_decisions.md` — canonical locked-decisions archive. Read before touching locked areas.
6. Any files referenced in `_resume.md` under "Read at session start" or "Next action".

Then — and only then — begin work on the user's request. If the `_aware_*.md` files look stale (last-refresh timestamp far in the past, or they describe behavior that doesn't match the code), run `/devlead awareness` before starting work.

## Dev work discipline — every code change traces to an intake entry

**Hard rule: no code change without an intake trace.** Every edit, new file, bug fix, or refactor must originate from an entry in `devlead_docs/_intake_*.md`. No exceptions.

- **Feature requests:** user says "add X" -> Claude captures to `_scratchpad.md` -> runs plugin planning (e.g. superpowers) -> `/devlead ingest <plan> --into _intake_features.md` -> implement.
- **Bugs Claude notices mid-task:** STOP the current edit. Append a new entry to `_scratchpad.md` describing the bug. Then `/devlead ingest --from-scratchpad <needle> --into _intake_bugs.md`. Only then fix the bug, with the new BUGS-NNNN ID referenced in the commit message.
- **Small inline cleanups:** same rule. If it's too small to warrant an intake entry, it's too small to do right now — leave a scratchpad note and move on.
- **Direct scratchpad -> intake:** for well-scoped items that don't need a full plugin-plan round-trip, use `/devlead ingest --from-scratchpad <needle> --into <file>` to promote in one step.

**Every intake entry must have at least one actionable item.** An entry with zero actionable items means the item wasn't thought through — refine or reject before promoting it toward the hierarchy. Later (Day 4+), intake entries get decomposed into BO/TBO/TTO nodes in `_project_hierarchy.md`, and every TBO must map to granular TTOs.

**What if the user insists on work without a pre-existing intake entry?** (e.g., "just fix this typo", "quick change to X"). DO NOT refuse; DO NOT silently skip; DO NOT do the work without a trace. Instead:

1. **Create the intake entry FIRST** (before touching any code) in the appropriate file — usually `_intake_bugs.md` for fixes or `_intake_features.md` for additions.
2. **Best-effort ID association:** look at existing intake entries and `_project_hierarchy.md` and link the new entry to any matching BO/TBO/TTO IDs it touches. If you can't tell, leave `proposed_bo` / `proposed_sprint` as `(needs BO)` / `(needs sprint)`.
3. **Mark the entry with `--forced`** so its `origin` field becomes `forced`. This feeds the future K_BYPASS KPI that measures how often discipline is bypassed.
4. **Then do the work.** Reference the new intake ID in the commit message.

Example: `/devlead ingest --from-scratchpad <needle> --into _intake_bugs.md --forced`

If you catch yourself about to edit code without an intake trace, **STOP** and follow the procedure above. No exceptions, no shortcuts — this rule is what prevents dark code.

### Backed by `/devlead gate`

The discipline rule is backed by `/devlead gate`. When `PreToolUse` fires without an `in_progress` intake entry, the gate writes a `gate_warn` audit event and injects a `systemMessage` nudge. Warn-only in v1; never exits non-zero. Enable by adding a `PreToolUse` hook to `.claude/settings.json` that invokes `devlead gate PreToolUse` — not auto-wired because the user opts in manually.

## Plugin bridge — how DevLead coexists with other plugins

DevLead does NOT replace or wrap other Claude Code plugins. When a task needs
planning, run the plugin's native flow unchanged (e.g. `superpowers brainstorming`
-> `writing-plans`), then call `/devlead ingest <plan-path> --type features|bug_issues`
to file the output into the matching `devlead_docs/_intake_*.md`. Every task must
trace back through scratchpad -> plan -> intake -> TTO -> BO -> Phase -> Vision.
Code without that trace is "dark code" and is forbidden.

See `docs/plugin-bridge.md` for the full flow and worked example.

## Legacy

The v1 codebase is archived untouched under `legacy/v1/`. It is **not** to be imported, referenced, or mined unless the user explicitly points at it. A git tag `v1-archive-2026-04-12` pins the last committed v1 state.

## Current state

- v2 source tree is empty stubs under `src/devlead/`.
- `devlead_docs/` is empty except for design docs the user has locked section by section.
- No tests yet. No CLI dispatch yet. No hooks wired yet.
- Next work happens only after the next design section is dictated and locked.

<!-- devlead:claude-md-start -->
## DevLead governance — read every session

This project uses **DevLead**, a governance tool that is the single channel
between you (the LLM) and the codebase. Every task traces through DevLead's
document store. These rules are non-negotiable.

### Session start — mandatory read order

At the start of **every** session, before doing anything else, read these files
in this exact order:

1. `devlead_docs/_resume.md` — thin bootstrap cursor (~30-50 lines): current
   focus, read order, next action, open blockers.
2. `devlead_docs/_intake_*.md` — scan for entries with `status: in_progress`.
   Those are the current focus. Run `/devlead focus show` to list them.
3. `devlead_docs/_aware_features.md` and `_aware_design.md` — auto-derived
   snapshots of what the code actually does right now.
4. `devlead_docs/_scratchpad.md` — raw untriaged capture from prior sessions.
5. `devlead_docs/_living_decisions.md` — canonical locked-decisions archive.

Then — and only then — begin work.

### Dev work discipline — no code without intake trace

**Hard rule:** every code change (edit, new file, bug fix, refactor) must
originate from an entry in `devlead_docs/_intake_*.md`. No exceptions.

- **New feature:** capture to `_scratchpad.md` → triage → ingest into
  `_intake_features.md` → implement.
- **Bug noticed mid-task:** STOP. Append to `_scratchpad.md`. Run
  `/devlead ingest --from-scratchpad <needle> --into _intake_bugs.md`.
  Only then fix it.
- **User forces work without pre-existing intake:** create the intake entry
  FIRST with `--forced` flag, THEN do the work. Never refuse, never skip.

### Enforcement gate

The discipline rule is backed by `/devlead gate`. When a `PreToolUse` hook
fires without an `in_progress` intake entry, the gate writes a `gate_warn`
audit event and injects a systemMessage nudge. Warn-only — never blocks.

### Available commands

| Command | What it does |
|---------|-------------|
| `/devlead init` | Install DevLead on a project |
| `/devlead scratchpad` | List raw capture entries |
| `/devlead scratchpad archive` | Archive promoted entries |
| `/devlead intake` | List all intake file entries |
| `/devlead triage` | Walk scratchpad for routing |
| `/devlead ingest <plan> --into <file>` | Ingest a plugin plan into intake |
| `/devlead promote <needle> --to intake\|decision\|fact` | Route scratchpad entries |
| `/devlead focus [show\|clear\|<id>]` | Set/show/clear current work focus |
| `/devlead awareness` | Refresh `_aware_*.md` from code |
| `/devlead gate <HookName>` | Run enforcement gate (stdin JSON) |
| `/devlead migrate <src> <heading> --to <dest>` | Hash-checked content migration |
| `/devlead verify-links` | Check cross-references for broken refs |
| `/devlead audit recent [N]` | Print recent audit events |
| `/devlead config show` | Show resolved config |

### File categories in devlead_docs/

| Prefix | Role | Examples |
|--------|------|---------|
| `_intake_*` | Work backlog (features, bugs) | `_intake_features.md` |
| `_living_*` | Curated intent docs (decisions, goals) | `_living_decisions.md` |
| `_aware_*` | Auto-derived from code (regenerated) | `_aware_features.md` |
| `_project_*` | Project state (hierarchy, status) | `_project_hierarchy.md` |
| `_resume.md` | Session bootstrap cursor | |
| `_scratchpad.md` | Raw untriaged capture inbox | |

### SOT blocks

Every file in `devlead_docs/` opens with a `<!-- devlead:sot ... -->` metadata
block declaring its purpose, owner, lineage, and lifetime. DevLead reads these
to understand the file's role. Do not remove them.
<!-- devlead:claude-md-end -->
