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
## DevLead governance — auto-generated from devlead_docs/

<!-- This section is derived from devlead_docs/ files. Do not hand-edit. -->
<!-- Run `devlead init` or `devlead refresh-claude-md` to regenerate. -->

### Session start — mandatory read order

Read these files in order before doing anything else:

1. `devlead_docs/_resume.md`
2. `devlead_docs/_routing_table.md`
3. `devlead_docs/_intake_features.md`
4. `devlead_docs/_intake_bugs.md`
5. `devlead_docs/_aware_features.md`
6. `devlead_docs/_aware_design.md`
7. `devlead_docs/_scratchpad.md`
8. `devlead_docs/_living_decisions.md`

Then — and only then — begin work.

### Dev work discipline

**2026-04-14 - Dev work discipline (all code traces to intake)**

- Edit/Write is HARD BLOCKED (exit 2) when no intake entry has `status: in_progress`.
- To unblock: run `/devlead focus <intake-id>`.
- To create a forced entry: `/devlead ingest --from-scratchpad <needle> --into _intake_features.md --forced`.

### Enforcement

DevLead gate runs on every Edit/Write via PreToolUse hook.
- **Default mode: hard** — exit 2 blocks the tool call. Claude cannot proceed.
- Configurable via `devlead.toml` `[enforcement] mode = "hard"|"soft"|"warning"`.
- Exempt paths: devlead_docs/**, docs/**, *.md, commands/**, tests/**.

### Available commands

| Command | What it does |
|---------|-------------|
| `/devlead audit` | Inspect the DevLead audit log |
| `/devlead awareness` | Refresh DevLead self-awareness files (_aware_*.md) |
| `/devlead config` | Show the resolved DevLead configuration |
| `/devlead focus` | Set, show, or clear the current focus by flipping intake entry status |
| `/devlead gate` | Run the DevLead PreToolUse enforcement gate (warn-only) |
| `/devlead ingest` | Ingest a plugin's output plan/spec into a DevLead intake file |
| `/devlead init` | Install DevLead on the current project — creates devlead_docs/ with scaffolding and seeds the canonical source of truth. |
| `/devlead intake` | List current intake file entries |
| `/devlead migrate` | Hash-checked, reversible content migration between devlead_docs/ files |
| `/devlead promote` | Promote a scratchpad entry to an intake file, a decision log, or a living file |
| `/devlead scratchpad` | Append a raw capture entry to devlead_docs/_scratchpad.md - verbatim triage inbox, zero information loss. |
| `/devlead triage` | Walk untriaged _scratchpad.md entries and route each to its canonical home |
| `/devlead verify-links` | Walk cross-references in devlead_docs/ and report broken refs + orphans |

### File categories in devlead_docs/

| Prefix | Role | Files |
|--------|------|-------|
| `_intake_*` | Work backlog | _intake_bugs.md, _intake_features.md |
| `_living_*` | Curated intent docs | _living_decisions.md, _living_design.md |
| `_aware_*` | Auto-derived from code | _aware_design.md, _aware_features.md |
| `_project_*` | Project state | _project_hierarchy.md, _project_status.md |
| `_resume.md` | Session bootstrap (auto-generated) | |
| `_scratchpad.md` | Raw capture inbox | |
| `_routing_table.md` | Intent routing (the brain) | |

### Routing table — FOLLOW THIS FOR EVERY USER INPUT

Before responding to ANY user input, classify the intent against the
responsibilities below. If a match is found, follow the steps EXACTLY.
If no match, proceed as business-as-usual.

## R1 — Building work pipeline

**Owner:** DevLead
**Scope:** Creating, updating, and maintaining the BO → TBO → TTO hierarchy

**Triggers:** user mentions new BO, TBO, TTO, hierarchy, pipeline, work breakdown, decomposition, "add objective", "break this down", "promote to hierarchy", "create a sprint"

**Steps:**
1. READ `devlead_docs/_project_hierarchy.md` — understand current hierarchy state
2. READ `devlead_docs/_intake_features.md` — find the source intake entry being promoted
3. VALIDATE — every TBO must have at least one TTO; every TTO must have a weight; weights within a parent must sum to 100
4. WRITE new or updated BO/TBO/TTO node into `_project_hierarchy.md`
5. WRITE update to the source intake entry's `promoted_to` field
6. WRITE `_audit_log.jsonl` event: `hierarchy_update`

**Guard:** No BO without at least one TBO. No TBO without at least one TTO. Weights must sum to 100 per parent. BO must have `start_date` and `end_date`.

---

## R2 — No coding outside intake context

**Owner:** DevLead
**Scope:** Ensuring every code change traces to an intake entry

**Triggers:** user asks to edit code, fix bug, refactor, create file, implement feature, write tests, modify any source file

**Steps:**
1. READ all `devlead_docs/_intake_*.md` — check for entries with `status: in_progress`
2. IF none found → STOP. Tell user: "No active intake focus. Run `/devlead focus <intake-id>` to set one, or capture this as a new intake entry first."
3. IF found → verify the requested work relates to the focused intake entry
4. PROCEED with coding only after steps 1-3 pass
5. WRITE `_audit_log.jsonl` event: `gate_check` with the focused intake ID

**Guard:** Code editing is blocked (self-enforced) until an intake entry is in_progress. This is the discipline rule. No exceptions. If user forces it, create the intake entry FIRST with `--forced` origin, then proceed.

---

## R4 — Delivering BOs on time

**Owner:** DevLead
**Scope:** Tracking deadlines, detecting slips, enforcing change management

**Triggers:** user mentions deadline, due date, missed date, slip, delay, "when is this due", "revise date", "extend deadline", "are we on track", or DevLead detects `today > BO.end_date AND BO.status != done`

**Steps:**
1. READ `devlead_docs/_project_hierarchy.md` — find the referenced BO
2. CHECK if deadline is missed: `today > end_date` and BO is not marked done
3. IF missed:
   a. PRESERVE the original `end_date` as `actual_date: (missed YYYY-MM-DD)`
   b. ASK user for `revised_date` and `revision_justification`
   c. WRITE updated BO node with change-management fields
   d. WRITE `_audit_log.jsonl` event: `deadline_revision`
4. IF on track: report days remaining and convergence percentage

**Guard:** `revised_date` requires `revision_justification`. No silent slips. Every revision is an audit event.

---

## R5 — Project management

**Owner:** DevLead
**Scope:** Status, blockers, priorities, planning, progress tracking

**Triggers:** user asks about status, blockers, priorities, sprint planning, "what should I work on next", progress, burndown, "what's done", "what's left"

**Steps:**
1. READ `devlead_docs/_project_hierarchy.md` — compute convergence per BO/TBO
2. READ all `devlead_docs/_intake_*.md` — count pending/in_progress/done
3. READ `devlead_docs/_audit_log.jsonl` — last 20 events for activity summary
4. COMPUTE status: done TTOs / total TTOs per TBO, weighted convergence per BO
5. PRESENT summary to user in plain language
6. WRITE `_audit_log.jsonl` event: `status_query`

**Guard:** Status is computed from data, not from memory. DevLead never says "I think we're at 60%" — it computes 60% from the hierarchy checkboxes and weights.

---

## R6 — KPI generation

**Owner:** DevLead
**Scope:** Generating metrics from every DevLead action; reporting health

**Triggers:** user asks for KPIs, dashboard, report, metrics, health, "how are we doing", "show me the numbers", or at end of session

**Steps:**
1. READ `devlead_docs/_audit_log.jsonl` — event counts, gate_warn frequency
2. READ `devlead_docs/_project_hierarchy.md` — convergence from checkboxes + weights
3. READ all `devlead_docs/_intake_*.md` — throughput: pending/done/in_progress counts
4. COMPUTE KPIs across four categories:
   - **A. LLM Effectiveness:** K_BYPASS (forced-origin count), gate_warn frequency
   - **B. Delivery:** intake throughput, BO on-time rate, blocker count
   - **C. Project Health:** traceability (TTOs linked to intake), doc freshness
   - **D. Business Convergence:** weighted rollup from hierarchy
5. RUN `devlead report` to generate HTML dashboard
6. WRITE `_audit_log.jsonl` event: `kpi_generated`

**Guard:** KPIs are computed from data, never estimated. Every KPI has a formula and a data source. If the data doesn't exist, the KPI shows "no data" — never a guess.

---

## Unmatched intent — business as usual

If the user's intent does not match any responsibility above, Claude proceeds normally. DevLead does not interfere with general conversation, research, debugging discussions, or other non-governance activities.

However: if during BAU work Claude is about to edit a file, R2 still applies. R2 is always active, not just when explicitly triggered.

### Current project state (auto-derived)

```
Sprint: DevLead Works For Real — 0.0% converged (0/67 TTOs)
  BO-001: Claude cannot cheat — 0.0%
  BO-002: I always know where my project stands — 0.0%
  BO-003: Sessions never start from zero — 0.0%
  BO-004: DevLead pays for itself — 0.0%
Current focus: FEATURES-0002
```

<!-- devlead:claude-md-end -->
