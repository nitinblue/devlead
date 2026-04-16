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

**Currently in_progress:** SHIPPING. All 13 features (FEATURES-0001 through -0013) are done. The codebase is complete. Do NOT build more features. The next step is packaging and publishing DevLead as a Claude Code plugin to the marketplace.

**Last touched:** 2026-04-16 (Session 4 — full depth-phase implementation landed, bootstrap chain wired, session report built)

## Read at session start

1. `devlead_docs/_resume.md` (this file) — the cursor
2. `devlead_docs/_intake_*.md` — scan for `status: in_progress` to find current focus
3. `devlead_docs/_aware_features.md` + `_aware_design.md` — current code state (auto-derived, evolving category)
4. `devlead_docs/_scratchpad.md` — untriaged raw capture
5. `devlead_docs/_living_decisions.md` — canonical locked-decisions archive
6. `docs/memory_and_enforcement_design_2026-04-14.html` — depth-phase design analysis

## Next action

**Session 5: SHIP TO MARKETPLACE.** Do NOT build more features. The user (Nitin) is a non-coder who has been struggling for months to finish projects with Claude. DevLead is his product. Revenue target: May 8, 2026.

Steps remaining to ship:
1. Fix the hook commands — they say `python -m devlead gate SessionStart` but need PYTHONPATH set to the plugin's src/ directory. Test that hooks actually fire when DevLead is installed as a Claude Code plugin (not just in the dev repo).
2. Update plugin.json version to 0.2.0 (remove -dev suffix).
3. Write a README.md that sells the one-sentence pitch: "DevLead makes Claude accountable. Install it, and every session ends with a plain-English report showing what Claude actually did — not what Claude claims it did."
4. Push to GitHub. Submit to Claude Code plugin marketplace.
5. Test by installing DevLead on one of Nitin's other 9 projects and running a real session.

**CRITICAL CONTEXT FOR NEXT CLAUDE:** Nitin cannot read Python. He is the product owner, not a developer. Do not ask him to verify code. Do not show him Python. The session report (`devlead report`) is how he verifies — it's an HTML file he opens in a browser. If you say "done," run `devlead report` and let the report prove it.

## Open blockers

None at session start.

## Historical content

Pre-depth-phase `_resume.md` (654 lines; locked decisions, open threads, hierarchy diagrams, PMS design, scratchpad feature spec) is preserved verbatim in `devlead_docs/_resume_archive_2026-04-14.md`. It will migrate into dedicated files (`_living_decisions.md`, `_living_design.md`, `_living_open_questions.md`) once the migration protocol (`/devlead migrate`) is built. Until then, treat the archive as the authoritative source for any historical decision not yet in `_living_decisions.md`.
