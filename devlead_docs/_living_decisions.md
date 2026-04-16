# Living Decisions

<!-- devlead:sot
  purpose: "Canonical append-only archive of all locked decisions"
  owner: "user+claude"
  canonical_for: ["locked_decisions"]
  lineage:
    receives_from: ["_scratchpad.md (via /devlead promote --to decision)"]
    migrates_to: []
  lifetime: "permanent"
  last_audit: "2026-04-15"
-->


> **Purpose.** Canonical append-only archive of all locked decisions on this
> project: architecture, scope, pricing, tooling, design, anything. Every
> entry is dated. Entries are never deleted. If a decision is reversed or
> refined, a new entry supersedes the old one - history remains intact.
>
> **This file is the canonical source.** Neither `_resume.md` nor any other
> file holds locked decisions. `_resume.md` is a thin session-bootstrap
> cursor. Locked decisions live here.
>
> **Contrast with other living files:**
> - `_living_project.md` - what the project IS (identity)
> - `_living_goals.md` - narrative goal descriptions (doc-only, no metrics)
> - `_living_design.md` - HOW the system is shaped (design intent)
> - `_living_decisions.md` - choices that got made, and why (this file)

---

## Log

## 2026-04-12 - Hierarchy (revised 2026-04-14)
- **Decision:** `Sprint -> BO -> TBO -> TTO`. Vision removed from the hierarchy. Phase renamed to Sprint.
- **Rationale:** Simplified from v2's original `Vision -> Goals -> Phase -> BO -> TBO -> TTO`. Vision was too aspirational for a week-to-week scope. Goals folded into a doc-only container (see below). Phase renamed to Sprint for memorability; DevLead's Sprint is scoped to ship-windows/versions (months), NOT the agile 2-week cadence.
- **Status:** locked
- **Supersedes:** v2 original hierarchy

## 2026-04-14 - Goals as doc-only container (not a hierarchy node)
- **Decision:** Goals is a loose documentation concept that groups BOs for human readability. It is NOT a metric-carrying hierarchy node. `_living_goals.md` is prose-only - no schema, no metric fields, no convergence rollups.
- **Rationale:** Earlier "BO = Goal (merged)" was wrong. A Goal is meta-narrative ("ship first revenue"); a BO is measurable ("sell X units by Y date"). Separating them allows loose goal framing without metric overhead.
- **Status:** locked
- **Supersedes:** "BO = Goal (merged)" from earlier Session 3

## 2026-04-14 - Plugin Bridge: zero-disruption principle
- **Decision:** DevLead NEVER modifies any Claude Code plugin's workflow, file paths, or defaults. Plugins run unchanged; DevLead ingests their outputs downstream into `_intake_*.md`.
- **Rationale:** Preserves user muscle memory. Avoids fragile wrapping. Single source of truth is enforced via ingestion, not via plugin modification.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - File recognition by prefix
- **Decision:** DevLead recognizes files by prefix: `_intake_*`, `_living_*`, `_project_*`, `_aware_*`. Users can create any number of files per category with any slug. Install ships starter templates only; the taxonomy is open.
- **Rationale:** Creative freedom. Users name files however fits them. DevLead just needs the prefix for routing.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - Self-awareness framework
- **Decision:** DevLead maintains `_aware_*.md` files that describe the project's current state auto-derived from code. v1 ships `_aware_features.md` and `_aware_design.md`. These are primary LLM memory substrate alongside `_resume.md` and `_scratchpad.md`.
- **Rationale:** Reduces reliance on `CLAUDE.md` as the only memory source. Projects become self-aware: what features exist, what modules exist, what depends on what, all derived from the code itself.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - Intake schema is template-driven
- **Decision:** Intake entries follow a template that defines allowed fields. Templates live in `devlead_docs/_intake_templates/*.md`. v1 ships one template (`default.md`); users can pick from multiple templates as more are added in v1.1+.
- **Rationale:** LLM drafts all fields at ingest; user only confirms/corrects placement at triage. The template constrains what fields exist so the schema isn't open-ended.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - Dev work discipline (all code traces to intake)
- **Decision:** Every code change must trace to an entry in `_intake_*.md`. If the user forces work outside normal flow, Claude creates the intake entry first (best-effort ID association with existing hierarchy/intake), marks it `--forced` (setting `origin: forced`), then does the work.
- **Rationale:** Prevents dark code. All work is traceable. The `origin: forced` field feeds a future K_BYPASS KPI measuring discipline slippage.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - Enforcement: configurable, three modes
- **Decision:** Dev-work discipline enforcement is a config knob in `devlead.toml` (or `.yml`) with three values: `warning` (advisory systemMessage via hook; never blocks), `soft` (exit 1; blocks but overridable), `hard` (exit 2; blocks until resolved). Default at install is `warning`.
- **Rationale:** Different teams want different rigor. Configurability honors both "minimum friction" and "maximum control" preferences. Default matches the locked "nothing exits 2 by default" rule.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - _resume.md is a thin bootstrap cursor
- **Decision:** `_resume.md` holds ONLY session-bootstrap information: current focus, read order, next action, open blockers. It does NOT hold locked decisions (see this file), open threads (future `_living_open_questions.md`), history, or design sections. Target ~30-50 lines maximum.
- **Rationale:** Original `_resume.md` grew to 654 lines at Session 3. Splitting concerns into dedicated canonical files keeps the bootstrap cursor small and scannable at session start. Historical content archived to `_resume_archive_2026-04-14.md` until the migration protocol ships.
- **Status:** locked
- **Supersedes:** All earlier `_resume.md` §3/§13/§4/§18/§19 responsibilities

## 2026-04-14 - Focus via intake entry status (not a separate file)
- **Decision:** Dev-work focus is tracked by flipping the `status` field inside an intake entry body to `in_progress`. No separate session-state file. `/devlead focus <intake-id>` sets it; `/devlead focus show` lists all `in_progress` entries; `/devlead focus clear` resets them all to `pending`.
- **Rationale:** The intake entry already has a `status` lifecycle field. Adding a parallel `_session_state.json` creates two sources of truth that can drift. Status-in-body means focus is naturally visible when reading the intake file, and multiple entries can be `in_progress` simultaneously (a feature + a related bug, etc.).
- **Status:** locked
- **Supersedes:** Earlier `_session_state.json` proposal and the "CWI (Current Working Intake)" framing from the design analysis

## 2026-04-14 - Config file format: TOML via stdlib tomllib
- **Decision:** Config files use TOML, parsed via Python's stdlib `tomllib` (Python 3.11+). Zero external dependencies. YAML is also permitted for files where nested structure is more natural.
- **Rationale:** Zero-dep footprint. TOML is human-friendly for flat config. YAML is available when needed.
- **Status:** locked
- **Supersedes:** (none)

## 2026-04-14 - Scratchpad routing has three targets
- **Decision:** Scratchpad entries are routed to one of three destinations during triage: (a) work -> `_intake_*.md`, (b) decision -> `_living_decisions.md`, (c) fact/doc -> `_living_*.md`. Implemented via `/devlead promote <needle> [--into <file>|--to decision|--to fact --into <file>]`.
- **Rationale:** Not all scratchpad content is work. Decisions and facts have their own canonical homes. Single-target promotion would force-fit content into intake files, creating clutter.
- **Status:** locked
- **Supersedes:** Earlier single-target `/devlead ingest --from-scratchpad` framing (still works as alias)
