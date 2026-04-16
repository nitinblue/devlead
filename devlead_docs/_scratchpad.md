# _scratchpad.md - DevLead raw capture / triage inbox

<!-- devlead:sot
  purpose: "Raw untriaged capture inbox"
  owner: "claude+user"
  canonical_for: ["raw_capture"]
  lineage:
    receives_from: ["session dialogue"]
    migrates_to: ["_intake_*.md", "_living_decisions.md", "_living_*.md"]
  lifetime: "permanent"
  bloat_cap_lines: 500
  last_audit: "2026-04-15"
-->


> **Purpose.** This file is the project's **raw capture space**. Anything the user says that doesn't yet have a dedicated home lands here verbatim (or close to it), so nothing is lost while DevLead figures out where it belongs. As items find proper homes (design docs, locked decisions in `_resume.md`, living files, intake files, `CLAUDE.md`), they get triaged OUT of here - hash-verified, audited, zero information loss.
>
> **Contrast with `_resume.md`.** `_resume.md` holds **session-to-session memory** - the handoff pointer for the next session, locked decisions, open threads, "where we are right now." `_scratchpad.md` holds **raw untriaged dumps** from any given session. Both exist, both are permanent, both are read every session. The goal is to keep `_scratchpad.md` as lean as possible.
>
> **Filename:** `devlead_docs/_scratchpad.md`

---

## Entry - 2026-04-14 - Plugin Bridge and Intake Flow

> Nitin dictated the bridging pattern between DevLead and other Claude Code plugins. Captured raw here; full design drafted in plan mode, implemented in Session 3 (this session). On completion this entry migrates OUT to `devlead_docs/_design_section2_plugin_bridge.md`.

### Principles (load-bearing)

1. **DevLead is the single source of truth for the project's work backlog.** Every task that ever gets executed must trace to a node in `devlead_docs/`.
2. **Zero disruption to plugin workflows.** DevLead does NOT modify, override, or replace how any Claude Code plugin operates. Superpowers' `brainstorming -> specs -> writing-plans` flow stays exactly as it is. Other plugins stay exactly as they are. Users' existing muscle memory is preserved.
3. **Plugins write to their native space; DevLead ingests downstream.** Superpowers writes to `docs/superpowers/specs/` and `docs/superpowers/plans/` - unchanged. DevLead picks up the actionable outputs AFTER and files them into `devlead_docs/_intake_*.md`, from which they flow into the BO/TBO/TTO hierarchy.
4. **No dark code.** Every line of code that gets written must trace back through: intake file -> TTO -> TBO -> BO -> Phase -> Vision. Code without that trace is "dark" - DevLead must detect it (v1 warn, v1.1 optional block).

### The flow (Nitin's dictation)

```
1. Raw dump of notes        -> _scratchpad.md
                                  |  triage (continuous)
                                  v
2. Item picked for backlog  -> Claude runs the standard plugin flow
                                (e.g. superpowers brainstorming -> spec ->
                                 writing-plans -> plan). Unchanged.
                                  |  bridge (DevLead's new job)
                                  v
3. Plan's actionable items  -> _intake_*.md
                                  |  promotion (design TBD)
                                  v
4. Backlog                  -> _project_hierarchy.md (BO / TBO / TTO)
                                  |  normal DevLead flow
                                  v
5. Code execution           -> traces all the way back up to the
                                originating note in _scratchpad.md
```

### Intake files - initial set (Nitin named these)

| File | What it holds |
|---|---|
| `_intake_features.md` | New feature requests ready to be planned |
| `_intake_bug_issues.md` | Bugs / issues / defects ready to be planned |
| *(others TBD in plan mode)* | |

### Status of this entry

- Load-bearing principles promoted to `_resume.md` Section 3 (locked decisions).
- Open mechanism questions promoted to `_resume.md` Section 13 (open threads).
- Plan written to `C:\Users\nitin\.claude\plans\iridescent-fluttering-sloth.md` and approved.
- Implementation landed Session 3 (2026-04-14). Ingested as INTF-0001 in `_intake_features.md`.
- This entry will migrate OUT to `_design_section2_plugin_bridge.md` on Day 4; until then it remains here for traceability.

---

## Entry - 2026-04-14 - Hierarchy simplification, Sprint rename, template-driven intake

> Nitin dictated a set of simplifications to the intake / hierarchy layer in Session 3.
> All captured raw here; locked rows were added to `_resume.md` Section 3 and the
> code refactor was executed immediately.

1. **Vision removed from the hierarchy.** New hierarchy is `Sprint -> BO -> TBO -> TTO`.
2. **BO = Goal (merged).** BOs are now goals with target dates. No separate Goals
   layer. K8 "Goal Yield" -> K8 "BO Yield".
3. **Top container renamed from "Phase" to "Sprint".** DevLead's Sprint is
   scoped to ship-windows / versions (months), NOT the agile 2-week cadence.
   Docs must be explicit about this to prevent confusion. Flagged as open thread
   for monitoring.
4. **Intake schema: lean + template-driven.** Claude drafts every field at
   ingest (title, summary, actionable items, proposed BO/Sprint/weight).
   User only confirms or corrects placement at triage. Onus is on the LLM;
   user's cognitive load is near-zero.
5. **Templates are real files on disk.** They cannot be open-ended - every
   intake file follows a template that defines allowed fields, owners,
   required/optional, defaults. Templates live in
   `devlead_docs/_intake_templates/*.md` as editable markdown files.
   **v1 ships ONE template (`default.md`)** - all intake files use it.
   Users pick from multiple templates as more are added in v1.1+.
6. **Template auto-update loop (v1.1).** Over time, DevLead should watch user
   behavior - fields always left blank, fields user adds manually, wording
   changes - and propose template updates. v1 ships static templates; the
   learning loop is deferred to v1.1 (open thread in `_resume.md` Section 13).
7. **File recognition by PREFIX, not hardcoded filenames.** DevLead globs
   `_intake_*.md`, `_living_*.md`, `_project_*.md`. Users can create as many
   files per category as they want, with any slug. Install ships starter
   templates only.
8. **Intake ID prefix derived from filename slug** (uppercased, hyphen-separated).
   `_intake_features.md` -> `FEATURES-NNNN`, `_intake_security_findings.md` ->
   `SECURITY-FINDINGS-NNNN`. No hardcoded prefix constants.

### Implementation landed this session

- `intake.py` rewritten: dataclass has new fields (proposed_bo, proposed_sprint,
  proposed_weight, promoted_at); `prefix_from_path()` derives ID; heading regex
  accepts any uppercase-alnum-hyphen prefix; `template_path_for()` locates the
  template file for a given intake file.
- `bridge.py` rewritten: `ingest(plan, into_file, docs_dir)` signature; validates
  that `into_file` matches `_intake_*.md`.
- `cli.py` rewritten: `/devlead ingest <plan> --into <file>` (was `--type`);
  `/devlead intake` lists all `_intake_*.md` files (not a fixed set).
- `install.py` rewritten: nested-path support; copies template files into
  `_intake_templates/`; renamed `_intake_bug_issues.md` -> `_intake_bugs.md`.
- Scaffold templates: new `_intake_bugs.md.tmpl`, `_intake_templates/{features,
  bugs,_default}.md.tmpl` template spec files.
- Commands `/devlead ingest` and `/devlead intake` updated in `commands/*.md`.

### Status of this entry

- Principles locked in `_resume.md` Section 3.
- Open threads in `_resume.md` Section 13 (Section 4 stale, goals redundancy,
  template auto-update loop, Sprint/agile collision, template versioning).
- Code + templates + docs updated in the same session.
- Migrates OUT to `_design_section3_intake_templates.md` on Day 4.

---

## Entry - 2026-04-14 - Self-awareness framework (reduce CLAUDE.md reliance)

> Nitin dictated a new in-built DevLead feature: projects running on DevLead
> should become **self-aware**. Start slow. Eventually: DevLead knows the
> technical design, patterns used, KPIs per feature, and every behavior
> DevLead introduces. **LLM should not rely solely on CLAUDE.md for memory;
> DevLead should give a very structured source of information for LLM memory.**

### Framework (v1)

1. **Concept.** A project is self-aware when DevLead continuously maintains
   a structured, code-derived description of the CURRENT state (features,
   design, patterns, metrics) separate from the curated `_living_*` files.
2. **File convention.** `devlead_docs/_aware_*.md`. Flat, prefixed,
   machine-generated, never hand-edited. Overwritten on every refresh.
3. **Source of truth.** The CODE. Awareness files are always re-derivable.
4. **LLM session-start read order (new):**
   `_resume.md` -> `_scratchpad.md` -> `_aware_*.md` -> work.
5. **Distinction from `_living_*`:**
   - `_living_*.md` = intent (design goals, decisions, glossary) - curated.
   - `_aware_*.md` = reality (what the code actually does now) - derived.

### Implemented this session (v1)

- `src/devlead/awareness.py` - pure scanner, stdlib only, no LLM calls.
- `/devlead awareness` command (refreshes both aware files).
- `_aware_features.md` - inventory of slash commands with description, command
  file, and handler function.
- `_aware_design.md` - inventory of Python modules with purpose (from
  docstring), public API, line count, internal dependencies.
- Scaffold placeholders ship at install time; refresh fills them in.
- `CLAUDE.md` session-start read order updated.

### Deferred to v1.1

- `_aware_metrics.md` - live KPI values
- `_aware_dependencies.md` - cross-module dependency graph
- `_aware_invariants.md` - things that must stay true
- Auto-refresh on Stop hook (so files stay current without manual calls)
- Trace-to-TTO auto-linking (awareness file cross-references to BO/TBO/TTO IDs)
- Template-driven aware file schema (like intake templates)

### Status

- Principles captured in `_resume.md` Section 3 as locked rows.
- Implementation landed in this session.
- Dogfood: run `/devlead awareness` on DevLead's own repo to populate both
  aware files.
- Migrates OUT to `_design_section4_self_awareness.md` when Day 4 store layer
  lands.

> **Promoted:** tracked as `FEATURES-0002` in `_intake_features.md`.

> **Promoted:** tracked as `FEATURES-0002` in `_intake_features.md`.

---

## Entry - 2026-04-14 - Scratchpad to intake conversion + dev-work discipline

> Last feature before Nitin freezes dev work to shake-the-tree test DevLead
> on itself. Two pieces:

### 1. Scratchpad -> intake conversion

- New: `/devlead ingest --from-scratchpad <needle> --into <_intake_file.md>`
- `<needle>` matches substring on scratchpad entry_id or title. First match
  in file order wins.
- Converts the scratchpad entry directly into an intake entry - no plugin
  plan round-trip needed for well-scoped items.
- Bidirectional trace: new intake entry records `source: scratchpad:<entry-id>`;
  scratchpad entry gets a `> **Promoted:**` cross-reference line appended.
- Implemented via `scratchpad.get_entry()`, `scratchpad.append_cross_reference()`,
  and `bridge.ingest_from_scratchpad()`.

### 2. Dev-work discipline rule

- Hard rule in `CLAUDE.md`: every code change must trace to an entry in
  `_intake_*.md`. No exceptions.
- Bugs Claude notices mid-task force a STOP:
  1. Append a new entry to `_scratchpad.md` describing the bug.
  2. Run `/devlead ingest --from-scratchpad <needle> --into _intake_bugs.md`.
  3. Only then fix the bug, with the new BUGS-NNNN ID in the commit message.
- Small inline cleanups follow the same rule. No "this is just a one-liner"
  exemptions - if it's too small to warrant an intake entry, it's too small
  to do right now; leave a scratchpad note and move on.
- Advisory in v1 (warnings + CLAUDE.md rule). Hook-based blocks land in v1.1.

### 3. Actionable-items floor

- Every intake entry must have >= 1 actionable item.
- Zero-item entries trigger a warning at ingest time:
  "every TBO must map to granular TTOs - refine or reject before promoting"
- This is the v1 version of "TBOs must map to granular TTOs". Full mapping
  enforcement lands when the store layer ships (Day 4+).

### Refinements (added mid-session by Nitin)

---

## Entry - 2026-04-14 - Memory cohesion and enforcement design analysis (depth phase kickoff)

> Nitin called development freeze after Session 3. Pivot from breadth (new
> features) to depth (cohesiveness, tightness, flexibility, configurability,
> agility, gracefulness). Two phase objectives:
>
> 1. Memory model cohesion: clutter-less, leak-free, full lineage.
> 2. Enforcement design: how DevLead gracefully overrides LLM behavior so that
>    _intake files remain the source of truth and no code gets written without
>    a traceable entry.
>
> This analysis is itself forced work (Nitin dictated; no pre-existing intake
> entry). Per the discipline rule I just shipped, Claude creates the intake
> entry first, associates IDs best-effort, marks --forced, THEN does the work.

### Actionable items

- [ ] Audit every file in devlead_docs/ for purpose, owner, lifetime, status
- [ ] Identify all leakage points (duplications, contradictions, stale content)
- [ ] Map full content lineage (where info enters, transforms, exits)
- [ ] Propose source-of-truth declaration block pattern
- [ ] Propose lineage metadata extension for all file types
- [ ] Propose migration protocol with zero-loss guarantee
- [ ] Propose _resume.md bloat discipline with cap + migration nudges
- [ ] Enumerate enforcement override levels 0-5 with tradeoffs
- [ ] Recommend v1 enforcement mechanism (hook-based systemMessage, Level 2)
- [ ] Design CWI (current working intake) tracking mechanism
- [ ] Draft devlead.yml config surface for memory + enforcement + audit
- [ ] Design audit log schema and /devlead audit subcommand
- [ ] Produce comprehensive HTML analysis document for user review
- [ ] List open questions for Nitin to answer before implementation begins

### Context pointers

- Current state post-Session 3: 23 scaffold files, 6 CLI commands, 6 modules
- Discipline rule now in CLAUDE.md; --forced flag ships with origin field
- Next session will be shake-the-tree testing, not new features
- Best-effort ID associations: plugin bridge principles in §3 + self-awareness
  row in §3 + forced-work procedure in §3 (all directly relevant)

> **Promoted:** tracked as `FEATURES-0003` in `_intake_features.md`.

---

## Entry - 2026-04-14 - Depth phase implementation (session 3 close-out)

> Nitin said "go ahead and implement all these" - meaning the clean-slate flow
> changes from the design analysis. This session lands the code. Next session
> is shake-the-tree test.

### Actionable items

- [x] Archive current _resume.md to _resume_archive_2026-04-14.md (manual zero-loss)
- [x] Write src/devlead/session.py (SessionState + Focus + load/save/set_focus)
- [x] Add /devlead focus command in cli.py
- [x] Add /devlead promote command in cli.py + bridge.promote_to_living
- [x] Fix L12: append_cross_reference dedupe in scratchpad.py
- [x] Overwrite _resume.md with thin cursor
- [x] Populate _living_decisions.md with initial locked decisions
- [x] Rewrite _living_goals.md as doc-only container
- [x] Update scaffold/_resume.md.tmpl (thin cursor template)
- [x] Add scaffold/_session_state.json.tmpl
- [x] Update install.py SCAFFOLD_FILES
- [x] Update CLAUDE.md session-start read order
- [x] Update commands/triage.md with 3-way routing
- [x] Create commands/focus.md
- [x] Create commands/promote.md
- [x] Dogfood: install, promote, focus, refresh awareness
- [x] Refresh docs/memory_and_enforcement_design_2026-04-14.html

### Context pointers

- FEATURES-0003 = design analysis intake (earlier this session)
- FEATURES-0004 = implementation intake (this work)
- Defaults locked per Nitin: TOML, L1/L2/L3/L12 first, /devlead focus naming

---

### (Original position of the refinements block below)

1. **Forced-work procedure.** When user pushes Claude to work outside the
   normal intake flow, Claude should NOT refuse and should NOT skip silently.
   Instead: (a) create the intake entry first, (b) best-effort associate IDs
   with existing hierarchy/intake items, (c) mark it `--forced` so
   `origin="forced"`, (d) then do the work. Trace integrity preserved.
2. **KPI tag for forced work.** The `origin` field is the v1 data model for a
   future K_BYPASS KPI that measures how often discipline is bypassed. v1
   ships the field; v1.1 wires the calculation.
3. **YAML permitted for configs.** User explicitly approved YAML as a valid
   format for future config files (alongside TOML). Decide per-file when the
   config layer ships.

### Post-implementation plan (Nitin's instructions)

- **FREEZE development** after this feature (with refinements above).
- Install DevLead on DevLead itself (already done; will re-verify rigorously).
- Shake-the-tree test: find gaps, friction, dark code paths.
- Audit what has been built and what is user-configurable.

### Status of this entry

- Principles in `_resume.md` Section 3 (4 new locked rows).
- Implementation landed in this session.
- Dogfood: convert the "self-awareness" scratchpad entry to
  `_intake_features.md` via `--from-scratchpad`.

> **Promoted:** tracked as `FEATURES-0001` in `_intake_features.md`.

## Entry - 2026-04-16 - DevLead responsibility chain and intent routing (Nitin dictation 2026-04-16)

Nitin dictated the core product definition for DevLead. This is the canonical source.

## DevLead has a defined role and responsibility set

Any user intent that resolves to one of DevLead's responsibilities triggers deterministic routing. Unresolved intents pass through to Claude as business-as-usual.

## DevLead responsibilities (load-bearing, Nitin-dictated)

1. **Building the pipeline of work** — BO -> TBO -> TTO mapping. The hierarchy is DevLead's job.
2. **No coding outside intake context** — All code traces to _intake entries. DevLead enforces this.
3. **Full ownership of flow, design, architecture, modularity** — DevLead knows the codebase. DevLead knows the design. DevLead knows the module boundaries. Not Claude.
4. **Delivering business objectives on time** — DevLead is accountable for deadlines, not Claude.
5. **Full project management suite** — Planning, tracking, prioritization, status, blockers — all DevLead.
6. **Everything DevLead does generates KPI data** — Every action produces data for KPI generation and reporting.

## Intent routing concept

- User says something -> DevLead classifies intent -> if intent matches a responsibility, DevLead routes to predefined file read/write sequence -> Claude executes
- If intent does not match any responsibility -> Claude proceeds as normal
- The responsibility chain is deterministic. Claude does not improvise inside DevLead's scope.

## Non-functional requirements

- Robust KPI generation and reporting framework
- Look up legacy/v1/ folder for features that were working fine (KPI engine, convergence, dashboard, etc.)

## Source

Nitin verbal dictation, 2026-04-16 session. Captured verbatim into scratchpad per DevLead discipline.

---
