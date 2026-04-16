# _resume.md

<!-- devlead:sot
  purpose: "Session bootstrap cursor: focus pointer, read order, next action, blockers"
  owner: "claude+user"
  canonical_for: ["session_bootstrap"]
  lineage:
    receives_from: ["_scratchpad.md (via triage)"]
    migrates_to: []
  lifetime: "permanent"
  bloat_cap_lines: 50
  last_audit: "2026-04-15"
-->


Session bootstrap cursor for DevLead itself. Target ~30-50 lines. Not history, not decisions, not open threads. Everything else lives in dedicated files.

> **Contrast.** Locked decisions live in `_living_decisions.md`. Design intent lives in `_living_design.md`. Raw untriaged capture lives in `_scratchpad.md`. Current code state lives in `_aware_*.md` (its own category, distinct from `_living_*`, and will keep evolving). Current focus is any intake entry with `status: in_progress`.

## Currently focused on

**Focus mechanism:** entries with `status: in_progress` in any `_intake_*.md` file are the current focus. Use `/devlead focus show` to list them. Use `/devlead focus <intake-id>` to set one.

**Currently in_progress:** FEATURES-0004 (Level-2 enforcement gate) — wave 1 of depth-phase implementation. FEATURES-0003 completed; design HTML refreshed 2026-04-15.

**Last touched:** 2026-04-15 (Session 4 — freeze lifted, depth-phase implementation underway)

## Read at session start

1. `devlead_docs/_resume.md` (this file) — the cursor
2. `devlead_docs/_intake_*.md` — scan for `status: in_progress` to find current focus
3. `devlead_docs/_aware_features.md` + `_aware_design.md` — current code state (auto-derived, evolving category)
4. `devlead_docs/_scratchpad.md` — untriaged raw capture
5. `devlead_docs/_living_decisions.md` — canonical locked-decisions archive
6. `docs/memory_and_enforcement_design_2026-04-14.html` — depth-phase design analysis

## Next action

**Session 4: depth-phase implementation in waves.** Freeze lifted 2026-04-15. Full intake sweep captured FEATURES-0004 through FEATURES-0013 from the HTML §0.4 deferred list.

- **Wave 1 (in flight):** FEATURES-0004 (gate) + -0009 (config) + -0010 (audit), FEATURES-0005 (SOT blocks), FEATURES-0012 (lazy living) — dispatched to 3 parallel subagents.
- **Wave 2 (next):** FEATURES-0006 (migrate), -0007 (lineage), -0008 (verify-links), -0011 (scratchpad archive).
- **Wave 3 (last):** FEATURES-0013 shake-the-tree dogfood test — validates the full stack after waves 1-2 land.

## Open blockers

None at session start.

## Historical content

Pre-depth-phase `_resume.md` (654 lines; locked decisions, open threads, hierarchy diagrams, PMS design, scratchpad feature spec) is preserved verbatim in `devlead_docs/_resume_archive_2026-04-14.md`. It will migrate into dedicated files (`_living_decisions.md`, `_living_design.md`, `_living_open_questions.md`) once the migration protocol (`/devlead migrate`) is built. Until then, treat the archive as the authoritative source for any historical decision not yet in `_living_decisions.md`.
