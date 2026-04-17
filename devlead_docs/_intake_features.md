# _intake_features.md

<!-- devlead:sot
  purpose: "Captured feature requests awaiting promotion to hierarchy"
  owner: "claude"
  canonical_for: ["feature_intake"]
  lineage:
    receives_from: ["_scratchpad.md", "plugin plans (superpowers etc.)"]
    migrates_to: ["_project_hierarchy.md"]
  lifetime: "permanent"
  last_audit: "2026-04-15"
-->


> **Intake file.** Captured feature requests awaiting promotion to the
> `Sprint -> BO -> TBO -> TTO` hierarchy in `_project_hierarchy.md`.
>
> **Flow:** `_scratchpad.md` (raw note) -> `/devlead triage` -> plugin planning
> flow (e.g. superpowers brainstorming + writing-plans) -> `/devlead ingest
> <plan> --into _intake_features.md` -> this file -> promotion to
> `_project_hierarchy.md`.
>
> **ID prefix:** derived from the filename slug. `_intake_features.md` ->
> `FEATURES-NNNN`. You can create additional intake files with any slug
> (`_intake_security.md` -> `SECURITY-NNNN`); DevLead recognizes any file
> matching `_intake_*.md`.
>
> **Template:** all intake files use `_intake_templates/default.md` in v1.
> As more templates ship, users will pick which template an intake file uses.

---

## Entries

*(No features captured yet. Run `/devlead ingest <plan> --into _intake_features.md` to add the first entry.)*

## FEATURES-0001 - Scratchpad to intake conversion + dev-work discipline
- **Source:** scratchpad:2026-04-14-scratchpad-to-intake-conversion-dev-work-discipline
- **Captured:** 2026-04-15T02:05:42Z
- **Summary:** > Last feature before Nitin freezes dev work to shake-the-tree test DevLead > on itself. Two pieces:
- **Actionable items:**
  - (none)
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0002 - Self-awareness framework (reduce CLAUDE.md reliance)
- **Source:** scratchpad:2026-04-14-self-awareness-framework-reduce-claude-md-reliance
- **Captured:** 2026-04-15T02:05:42Z
- **Summary:** > Nitin dictated a new in-built DevLead feature: projects running on DevLead > should become **self-aware**. Start slow. Eventually: DevLead knows the > technical design, patterns used, KPIs per feature, and every behavior > DevLead introdu
- **Actionable items:**
  - (none)
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0003 - Memory cohesion and enforcement design analysis (depth phase kickoff)
- **Source:** scratchpad:2026-04-14-memory-cohesion-and-enforcement-design-analysis-depth-phase-kickoff
- **Captured:** 2026-04-15T02:26:40Z
- **Summary:** > Nitin called development freeze after Session 3. Pivot from breadth (new > features) to depth (cohesiveness, tightness, flexibility, configurability, > agility, gracefulness). Two phase objectives: > > 1. Memory model cohesion: clutter-le
- **Actionable items:**
  - [x] Audit every file in devlead_docs/ for purpose, owner, lifetime, status
  - [x] Identify all leakage points (duplications, contradictions, stale content)
  - [x] Map full content lineage (where info enters, transforms, exits)
  - [x] Propose source-of-truth declaration block pattern
  - [x] Propose lineage metadata extension for all file types
  - [x] Propose migration protocol with zero-loss guarantee
  - [x] Propose _resume.md bloat discipline with cap + migration nudges
  - [x] Enumerate enforcement override levels 0-5 with tradeoffs
  - [x] Recommend v1 enforcement mechanism (hook-based systemMessage, Level 2)
  - [x] Design CWI (current working intake) tracking mechanism
  - [x] Draft devlead.yml config surface for memory + enforcement + audit
  - [x] Design audit log schema and /devlead audit subcommand
  - [x] Produce comprehensive HTML analysis document for user review
  - [x] List open questions for Nitin to answer before implementation begins
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0004 - Level-2 enforcement gate (devlead gate PreToolUse)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#recommend
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Ship the Level-2 enforcement gate designed in FEATURES-0003 HTML §6. Hook-invoked script reads stdin JSON, checks for an in_progress intake entry, writes an audit event, and returns a systemMessage nudge. Never blocks by default. Backs CLAUDE.md discipline rule with a programmatic signal.
- **Actionable items:**
  - [x] Create src/devlead/gate.py with check_pretooluse(hook_input) -> dict
  - [x] Wire `devlead gate <HookName>` subcommand in cli.py (stdin JSON in, stdout JSON out)
  - [x] Read in_progress intake entries via intake.list_by_status as the CWI equivalent
  - [x] Default exempt paths: devlead_docs/**, docs/**, *.md, commands/**, tests/**
  - [x] Warn-only mode always; never exit non-zero in v1
  - [x] Do NOT auto-wire .claude/settings.json hook — user opts in manually
  - [x] Update CLAUDE.md to reference devlead gate as the discipline signal source
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0005 - SOT declaration blocks (Proposal A)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#tighten (Proposal A)
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Every devlead_docs/ file opens with a structured SOT block (purpose, owner, canonical_for, lineage, lifetime, bloat_cap_lines, last_audit). Parsed by new src/devlead/sot.py. Closes leaks L5 (_living vs _aware confusion), L9 (no lifecycle semantics).
- **Actionable items:**
  - [x] Create src/devlead/sot.py with parse(path) and read_all(docs_dir)
  - [x] Define SOT block format (HTML comment wrapping YAML-ish key/value lines)
  - [x] Backfill SOT blocks into every existing scaffold template (src/devlead/scaffold/*.tmpl)
  - [x] Backfill SOT blocks into every existing devlead_docs/*.md in this repo
  - [ ] Add /devlead sot list|check command for inspection (deferred — CLI wiring is follow-up)
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0006 - Migration protocol /devlead migrate (Proposal C)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#tighten (Proposal C)
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Hash-checked, reversible content migration between files with zero-loss guarantee. Always strict mode — information loss is unrecoverable. Replaces the manual one-off archive approach used in Session 3.
- **Actionable items:**
  - [x] Create src/devlead/migrate.py with migrate(src_section, dest_file) and rollback
  - [x] Hash-check: destination must already contain matching content before removal
  - [x] Append every migration to devlead_docs/_migration_log.jsonl
  - [x] Wire /devlead migrate, /devlead migrate rollback <id>, /devlead migrate list in cli.py
  - [x] Update commands/migrate.md
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0007 - Lineage metadata on intake entries (Proposal B)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#tighten (Proposal B)
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Extend IntakeEntry with derived_from, descendants, supersedes fields. Enables graph walks and supersession tracking across intake/scratchpad/hierarchy nodes.
- **Actionable items:**
  - [x] Add derived_from, descendants, supersedes fields to intake.IntakeEntry
  - [x] Update intake.py serializer/parser to round-trip the new fields
  - [x] Update _intake_templates/default.md to include the new fields
  - [x] Populate automatically at ingest where possible (scratchpad entry -> derived_from)
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0008 - /devlead verify-links cross-reference walker
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#tighten (Proposal B follow-up, closes L10)
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Walk every cross-reference in devlead_docs/ (intake source fields, scratchpad cross-ref lines, hierarchy parent pointers, SOT lineage blocks). Report broken refs, orphans, dangling promotions. Writes to audit log.
- **Actionable items:**
  - [x] Create src/devlead/verify.py with verify_links(docs_dir)
  - [x] Build reference graph: intake.source, scratchpad promoted-to, SOT lineage.receives_from/migrates_to
  - [x] Detect broken refs (target missing) and orphans (not referenced by anyone)
  - [x] Wire /devlead verify-links in cli.py
  - [x] Emit audit events (verify_pass, verify_broken, verify_orphan)
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0009 - devlead.toml config loader (stdlib tomllib)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#config
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Single config surface at repo root. Loaded via stdlib tomllib (zero dep). Every knob in the design doc maps to a TOML section (memory, enforcement, audit, intake, bridge, kpis). Defaults live in code; TOML overrides.
- **Actionable items:**
  - [x] Create src/devlead/config.py with load(repo_root) -> Config
  - [x] Define defaults dict in code; tomllib parses devlead.toml if present
  - [x] Ship devlead.toml.tmpl in scaffold with commented-out defaults
  - [x] Make gate.py, migrate.py, audit.py all read config through this module
  - [x] Wire /devlead config show subcommand for inspection
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0010 - Audit log writes from all commands
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#audit
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** _audit_log.jsonl ships empty today. Every command (ingest, promote, focus, awareness, gate, migrate) should append a structured event. Schema locked per HTML §8.1.
- **Actionable items:**
  - [x] Create src/devlead/audit.py with append_event(docs_dir, event_dict)
  - [x] Lock schema: ts, event, tool, cwi, intake_id, source, origin, result, message
  - [x] Add audit.append_event calls in bridge.ingest, bridge.ingest_from_scratchpad, bridge.promote_to_living, cli._cmd_focus, awareness.refresh
  - [x] Add /devlead audit recent [N] inspection subcommand
  - [x] Unit test that each command writes exactly one event per invocation
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0011 - Scratchpad archival rule (L8, Q7)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#leaks (L8 + Q7)
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Scratchpad entries never retire even after promotion. Add rule: entries with a > Promoted: cross-reference can be archived to _scratchpad_archive.md after configurable grace (default 1 Sprint). Closes L8 and answers Q7.
- **Actionable items:**
  - [x] Add scratchpad.archive_promoted(path, grace_days) helper
  - [x] Write archived entries to devlead_docs/_scratchpad_archive.md with timestamp
  - [x] Wire /devlead scratchpad archive subcommand
  - [ ] Config knob: memory.scratchpad_archive_after_sprints in devlead.toml
  - [x] Never archive entries still referenced by in_progress intake entries
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0012 - Lazy living-file creation (L11)
- **Source:** docs/memory_and_enforcement_design_2026-04-14.html#leaks (L11)
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Eight of nine _living_*.md files ship as empty placeholders. Install feels like busywork. Ship only _living_project.md + _living_standing_instructions.md + _living_decisions.md. Others created on demand via /devlead init --add <slug>.
- **Actionable items:**
  - [x] Reduce SCAFFOLD_FILES in install.py to the three essential _living_*.md
  - [ ] Implement /devlead init --add <slug> for on-demand creation (deferred — install_addon() helper shipped; CLI wiring is follow-up)
  - [x] Keep the removed templates available in scaffold/ so --add can find them
  - [x] Update commands/init.md
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0013 - Shake-the-tree dogfood test (Session 4 planned)
- **Source:** devlead_docs/_resume.md#next-action
- **Captured:** 2026-04-15T04:00:00Z
- **Summary:** Install DevLead on a throwaway project and run the full user journey end-to-end: scratchpad capture -> triage -> promote (work / decision / fact) -> focus -> ingest -> awareness -> intake listing. Catalog every place that bends or breaks. File each gap as a _intake_bugs.md entry via /devlead promote --forced.
- **Actionable items:**
  - [ ] Create /tmp/devlead-shake-test fresh directory
  - [ ] Run /devlead init
  - [ ] Run every command in the user journey and note friction points
  - [ ] File each friction point as a BUGS-NNNN entry via /devlead promote --forced
  - [ ] Write findings summary to devlead_docs/_scratchpad.md
  - [ ] Run after FEATURES-0004 through -0012 land (validates the new stack)
- **Proposed BO:** (needs BO)
- **Proposed Sprint:** (needs sprint)
- **Proposed weight:** (needs weight)
- **Status:** done
- **Origin:** forced
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0014 - Convergence math layer (Phase 1 BO-1)
- **Source:** docs/devlead-vision-2026-04-16.html#tab4 + #tab5 (BO-1 of Phase 1)
- **Captured:** 2026-04-17T22:00:00Z
- **Summary:** Ship the convergence math engine end-to-end on DevLead's own project. Pure-math `convergence.py` module + tests, then BO/TTO schema extensions for `metric / baseline / target / metric_source / intent_vector`, then promise-ledger writer wired into the verifier, then a `metric_source: manual` adapter so one BO can compute a real C(τ) from a real metric reading. This delivers Tab 5 BO-1 ("Convergence math runs on a real metric") within ~10 engineering days.
- **Actionable items:**
  - [x] Step 2: src/devlead/convergence.py — 190 LOC, 40 tests
  - [x] Step 3: tests/test_convergence.py — Tab 4 worked numbers pinned
  - [x] Step 4: BO + TTO schema extensions, parser updates, backward-compat (18 tests)
  - [x] Step 5a: promise-ledger writer in verifier.py
  - [x] Step 5b: realisation sweep — computes φ/ε at window expiry, classifies regime
  - [x] Step 6: metric_source: manual mode + history overlay (16 tests)
  - [x] Dashboard: Convergence panel in dashboard.py (renders C, G, per-BO, promise/realisation)
  - [x] Verify: convergence.py 40 tests pass, BO-001 instrumented, real C(τ) = 3.1% computed
- **Proposed BO:** (Phase 1 BO-1 per Tab 5)
- **Proposed Sprint:** Phase 1 (3 weeks from 2026-04-17, deadline 2026-05-08)
- **Proposed weight:** 0.30
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0015 - project-init CLI (Phase 1 BO-2)
- **Source:** docs/devlead-vision-2026-04-16.html#tab5 (BO-2 of Phase 1)
- **Captured:** 2026-04-17T04:10:00Z
- **Summary:** Ship `devlead project-init` — the cold-start onboarding CLI. Interactive 10-question interview captures structured answers about a project; a "lock" subcommand hashes the resulting hierarchy and writes it to `_living_decisions.md` plus auto-generates `_intake_features.md` and `_intake_nonfunctional.md` from the TTOs. The Claude-in-the-loop drafting step (free-form answers → BO/TBO/TTO draft) is documented but executed by Claude in the user's session, not embedded as an LLM call in DevLead itself. v1 closes the blank-page problem without shipping LLM dependencies.
- **Actionable items:**
  - [x] src/devlead/project_init.py — 292 LOC, 21 tests
  - [x] tests/test_project_init.py — interview, lock idempotency, generate_intake split by ttype
  - [x] cli.py — `devlead project-init [lock|generate-intake]` dispatch
  - [x] Verify: lock produced hash `e149c98e52c5` on this repo's hierarchy; generate-intake derived 42 functional + 10 non-functional entries
- **Proposed BO:** (Phase 1 BO-2 per Tab 5)
- **Proposed Sprint:** Phase 1 (deadline 2026-05-01)
- **Proposed weight:** 0.25
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0017 - Auto session hand-off in _resume.md (anti-amnesia)
- **Source:** Nitin question 2026-04-17 — "can DevLead detect this and fix instead of claude"
- **Captured:** 2026-04-17T04:25:00Z
- **Summary:** Symptom: at session end, _resume.md said "No active focus" and listed STALE legacy TTOs as pending, while in reality FEATURES-0014/15/16 had just shipped today (~1140 LOC, 120 tests). A fresh Claude session reading _resume.md cold had no idea what was just built. Cure: enriched resume.py with three auto-derived sections — Recently shipped, Recent activity by intake (audit-derived), Untracked modules detected. Every section sourced from existing files; nothing hand-written. Session amnesia is now structurally impossible because the data was always there — just not rendered.
- **Actionable items:**
  - [x] resume.py: _recent_done_intake / _recent_active_cwi / _untracked_modules helpers
  - [x] resume.py.generate(): three new sections injected (top of file for Recently shipped, bottom for Untracked)
  - [x] tests/test_resume_enrichment.py — 13 tests including matcher edge-cases
  - [x] Verify: regenerated _resume.md now shows FEATURES-0014/15/16/17 under "Recently shipped" + per-CWI edit counts under "Recent activity"
- **Proposed BO:** (anti-amnesia / cross-cutting)
- **Proposed Sprint:** Phase 1 follow-up
- **Proposed weight:** 0.05
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0016 - Effort tracking wired (Phase 1 BO-3)
- **Source:** docs/devlead-vision-2026-04-16.html#tab5 (BO-3 of Phase 1) + Tab 3 trash card "Effort tracking exists but isn't wired"
- **Captured:** 2026-04-17T04:14:00Z
- **Summary:** The `effort.py` module is fully implemented (record_effort + aggregation) but nothing calls it. Wire `gate.check_pretooluse` to invoke `effort.record_effort` for each Edit/Write/MultiEdit attempt with the active CWI. Token count is NOT available from PreToolUse hooks in Claude Code, so v1 captures "edit count per TTO" as a cost-attribution proxy. Real token cost can be backfilled later from session-history if/when that data becomes accessible. Honest about the limit — surface as "edits per TTO" not "$ per TTO" until token cost is real.
- **Actionable items:**
  - [x] gate.check_pretooluse calls effort.record_effort with active CWI per gate_pass event
  - [x] tests/test_effort_wiring.py — 6 tests verifying CWI attribution, exempt skip, multi-CWI fan-out, accumulation
  - [x] Verify: edit to src/devlead/effort.py at 04:16:44Z wrote the first FEATURES-0016 row to _effort_log.jsonl, fully closed loop
- **Proposed BO:** (Phase 1 BO-3 per Tab 5)
- **Proposed Sprint:** Phase 1 (deadline 2026-05-08)
- **Proposed weight:** 0.10
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0018 - Solid _resume.md with surfaced next-move candidates
- **Source:** Nitin direction 2026-04-17 — "lets keep option fresh for next session, to be picked up from html from my point of view, but as part of devlead you need to have a solid _resume"
- **Captured:** 2026-04-17T04:35:00Z
- **Summary:** Next session will open with no active focus by design (Nitin will pick from Tab 6 candidates). Today's _resume.md surfaces 36 stale HIERARCHY-* pending entries that drown out the 5 strategic FEATURES-NNNN candidates. Fix: filter pending list to show FEATURES-NNNN first with one-line context, collapse HIERARCHY-* to a single count line, and add a one-line pointer to Tab 6 of the vision doc for full strategic context. Make _resume.md solid enough that picking next focus takes 30 seconds.
- **Actionable items:**
  - [ ] resume.py: split pending intake into FEATURES-NNNN (highlighted) vs HIERARCHY-* (collapsed count)
  - [ ] resume.py: add a "## Choose your next focus" section that lists pending FEATURES-NNNN with their summary line + suggested `/devlead focus <id>` command
  - [ ] resume.py: add a one-line pointer at top of file to Tab 6 of the vision HTML for strategic context
  - [ ] tests for the new pending-split and choose-your-focus behaviour
  - [ ] Verify: regenerated _resume.md shows FEATURES-0019..0023 prominently with focus commands ready to copy-paste
- **Proposed BO:** (anti-amnesia v2 / cross-cutting)
- **Proposed Sprint:** Phase 1 follow-up
- **Proposed weight:** 0.05
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0019 - TBO-I — Dashboard `_tab_dod` synchronous-verify hang fix
- **Source:** docs/devlead-vision-2026-04-16.html#tab6 (orthogonal small TBOs)
- **Captured:** 2026-04-17T04:35:00Z
- **Summary:** Today's full dashboard generation takes ~45 minutes because `_tab_dod` runs every TTO's `verify:` shell command synchronously. Fix: skip verify execution at dashboard render time (use cached results from last `devlead verify-all` run instead, or run with a hard timeout). Convergence panel works in isolation; full dashboard should also work in <5s. ~1 hour.
- **Actionable items:**
  - [x] Replace synchronous verify-runs in _tab_dod with audit-log cached results lookup
  - [x] Verify: `devlead dashboard` finishes in 0.491 seconds (down from ~45 minutes)
- **Proposed BO:** (core feature polish, post-Phase-1-shipped)
- **Proposed weight:** 0.03
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0020 - TBO-G — Stop hook auto-runs realisation-sweep + stale metric prompts
- **Source:** docs/devlead-vision-2026-04-16.html#tab6 (orthogonal small TBOs)
- **Captured:** 2026-04-17T04:35:00Z
- **Summary:** Today users must remember to run `devlead realisation-sweep` and `devlead metric-update` manually. Wire both into the Stop hook: at session end, sweep pending promise-ledger rows whose window has expired, and prompt if any BO metric is older than 7 days. Makes daily usage frictionless. ~30 min.
- **Actionable items:**
  - [x] gate.check_stop calls promise_ledger.run_realisation_sweep at end of every session
  - [x] Stop hook prompts owner when any BO metric reading is older than the BO's window
  - [x] Verify: ran `gate.check_stop` directly, session_end event written; silent when nothing pending or stale (correct behavior)
- **Proposed BO:** (core feature polish)
- **Proposed weight:** 0.03
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0021 - TBO-H — Promote FEATURES-0014..0017 into hierarchy as TTOs
- **Source:** docs/devlead-vision-2026-04-16.html#tab6 (orthogonal small TBOs)
- **Captured:** 2026-04-17T04:35:00Z
- **Summary:** Right now C(τ) = 3.1% is computed only on BO-001 (intake-trace %). The entire convergence framework work (FEATURES-0014..0017) lives in intake but not in `_project_hierarchy.md`. Promoting them as TTOs under appropriate TBOs would let the convergence math run on the very work that built convergence — closes the dogfood loop completely. ~1 hour. Best done together with TBO-G so realisation-sweep has more rows to evaluate.
- **Actionable items:**
  - [ ] Identify the right TBO under which FEATURES-0014..0017 belong (likely a new TBO-Phase1-shipped)
  - [ ] Add TTO entries with intent_vector field populated
  - [ ] Run convergence math, observe C(τ) reflects real shipped work
- **Proposed BO:** (core feature polish, dogfood loop)
- **Proposed weight:** 0.04
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0022 - TBO-J — Convergence dashboard explanatory UX
- **Source:** docs/devlead-vision-2026-04-16.html#tab6 (proposed core polish)
- **Captured:** 2026-04-17T04:35:00Z
- **Summary:** The convergence panel today shows numbers (C, G, α, φ, ε, regime labels) but not what they mean. Add inline tooltips, a one-line explainer per number, and color-coded regime badges. So opening the dashboard tells the user "this is good / this is concerning / this needs attention" without re-reading Tab 4. ~1-2 hours.
- **Actionable items:**
  - [ ] Add a header explanation block at top of Convergence panel
  - [ ] Each number gets a one-line "what it means" tooltip or aside
  - [ ] Regime label colour-coded (green=realised, orange=partial, red=vapor)
  - [ ] "What to do about this" hint per regime
- **Proposed BO:** (core feature polish, user experience)
- **Proposed weight:** 0.03
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0023 - TBO-K — Better `devlead resume` "next move" suggestion
- **Source:** docs/devlead-vision-2026-04-16.html#tab6 (proposed core polish)
- **Captured:** 2026-04-17T04:35:00Z
- **Summary:** Currently `_resume.md` says "No active focus" when nothing is in progress. It could derive a suggested-next from the highest-α pending TTO in the hierarchy, or the highest-priority pending FEATURES-NNNN intake entry. Smaller "what now?" friction. ~30 min. (Note: FEATURES-0018 partially addresses this for the FEATURES-NNNN case; this TBO extends it to hierarchy-derived suggestion.)
- **Actionable items:**
  - [ ] resume.py: when no active focus, derive a suggestion from highest-α pending TTO
  - [ ] If no hierarchy data, fall back to most-recently-added pending intake
  - [ ] Verify: clear focus, regenerate _resume.md, observe a sensible "Suggested next focus" line
- **Proposed BO:** (core feature polish, daily-driver UX)
- **Proposed weight:** 0.02
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0024 - MD render layer — `devlead render` produces HTML view per MD file
- **Source:** Nitin direction 2026-04-17 — "expose all the md documents as HTML, give visual feel for what command line does"
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** Foundation of the MD↔HTML loop. Every `devlead_docs/*.md` gets a rendered HTML file at `docs/views/<filename>.html`. Uses stdlib markdown rendering (or the `markdown` package if shipping is faster) plus the dashboard CSS so views look consistent. Static output; no daemon required for v1. The render command walks devlead_docs/, renders each MD, plus generates an index page linking to all of them. Read-only in v1; edit-back is FEATURES-0029.
- **Actionable items:**
  - [ ] src/devlead/render.py — markdown to HTML rendering (stdlib parser or `markdown` package)
  - [ ] `devlead render` CLI command writes HTML for every devlead_docs/*.md
  - [ ] Generated HTML uses dashboard's existing CSS variables and widget classes
  - [ ] Index page at docs/views/index.html lists every rendered file with one-line summary
  - [ ] tests/test_render.py — smoke test rendering on synthetic MD + integration on this repo's devlead_docs/
  - [ ] Verify: `devlead render` produces docs/views/_intake_features.html, _resume.html, etc., all viewable in browser
- **Proposed BO:** (MD↔HTML loop, foundation)
- **Proposed weight:** 0.10
- **Status:** done
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0025 - New `_living_*` content extracted from vision HTML tabs
- **Source:** Nitin direction 2026-04-17 — "see if you want to introduce any new md file category"
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** Today's vision HTML (Tabs 1-6) holds substantial content NOT captured in any MD file. Extract into 4 new `_living_*.md` files so the source-of-truth principle holds — LLMs read MD; HTML is the rendered view. Files: `_living_pitch.md` (problem, 4 layers, what DevLead is — Tab 1), `_living_vision.md` (target state, 3 deltas, architecture rings — Tab 2), `_living_buyer.md` (outside-perspective trust/distrust — Tab 3), `_living_demos.md` (worked walkthroughs — Tabs 4 + 5). Once these exist, the vision HTML becomes a generated artifact rendered from MD instead of the canonical source.
- **Actionable items:**
  - [ ] Draft `devlead_docs/_living_pitch.md` from Tab 1 content
  - [ ] Draft `devlead_docs/_living_vision.md` from Tab 2 content
  - [ ] Draft `devlead_docs/_living_buyer.md` from Tab 3 content
  - [ ] Draft `devlead_docs/_living_demos.md` from Tab 4 + Tab 5 content
  - [ ] Update SOT blocks on each new file
  - [ ] Update CLAUDE.md session-start read order to include new files
  - [ ] Verify: `devlead render` produces HTML views for each new MD
- **Proposed BO:** (MD↔HTML loop, content migration)
- **Proposed weight:** 0.06
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0026 - Auto-derived `_aware_status.md` post-implementation snapshot
- **Source:** Nitin direction 2026-04-17 + Tab 6 of vision HTML
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** Tab 6 ("Fresh look — post-implementation re-look") is content that should be auto-derived rather than hand-written. Like `_aware_features.md` and `_aware_design.md`, but for status / progress. Aggregates: done intake entries (recent), pending TBOs, convergence numbers, recent shipped LOC by audit log. Refreshed by `devlead awareness` alongside the existing aware files. Replaces hand-written status reports; users always see truth from data.
- **Actionable items:**
  - [ ] src/devlead/awareness.py: add render_status() function alongside render_features and render_design
  - [ ] _aware_status.md template with sections: shipped (last 30 days), pending TBOs, convergence summary, key counts
  - [ ] `devlead awareness` regenerates all three aware files
  - [ ] Tests for render_status produces stable output
  - [ ] Verify: `devlead awareness` produces _aware_status.md showing today's shipped work
- **Proposed BO:** (MD↔HTML loop, auto-derived content)
- **Proposed weight:** 0.04
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0027 - Documents index page in dashboard
- **Source:** Nitin direction 2026-04-17 — "give visual feel for what is being done in command line"
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** New "Documents" tab in the dashboard that lists every `devlead_docs/*.md` file with metadata (owner, purpose from SOT block, line count, last modified). Each row links to the rendered HTML view. Becomes the entry point users open when they want to see what is in DevLead's brain.
- **Actionable items:**
  - [ ] dashboard.py: add `_tab_documents(docs_dir)` function
  - [ ] Read SOT blocks via sot.read_all(docs_dir) to extract metadata
  - [ ] Render as table: filename, owner, purpose, lines, last_modified, view-link
  - [ ] Wire into tabs list
  - [ ] Verify: dashboard "Documents" tab shows all 20+ MD files with working links
- **Proposed BO:** (MD↔HTML loop, navigation)
- **Proposed weight:** 0.03
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0028 - Rich card-based HTML views for `_intake_*.md` files
- **Source:** Nitin direction 2026-04-17 (visual feel)
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** Generic markdown-to-HTML rendering (FEATURES-0024) treats intake files as plain text. Intake entries are highly structured — they deserve a card-based rich view: status badges (pending/in_progress/done with color), per-actionable-item checkboxes, progress bar per entry, source/promoted-to as clickable links. Builds on FEATURES-0024 renderer but adds intake-specific styling.
- **Actionable items:**
  - [ ] src/devlead/render.py: detect intake files (`_intake_*.md`), use specialised renderer
  - [ ] Each intake entry → card with status badge, summary, actionable items as checkboxes (visual only in v1)
  - [ ] Progress bar showing percent done actionable items per entry
  - [ ] Filter buttons (show only pending / in_progress / done)
  - [ ] Verify: rendered _intake_features.html shows all entries as visual cards
- **Proposed BO:** (MD↔HTML loop, rich rendering)
- **Proposed weight:** 0.04
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0029 - `devlead serve` daemon + edit-from-HTML capability
- **Source:** Nitin direction 2026-04-17 — "edit MD files right from HTML, this will be very powerful"
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** v2 of the MD↔HTML loop. Tiny stdlib http.server daemon on localhost:7777 that serves the rendered HTML views AND accepts edit-back POST requests. Each rendered HTML has form fields / inline-editable elements; on save, the daemon validates and writes MD. MD remains source of truth; HTML is the editing surface for users who do not want to open a text editor. Significant work — properly belongs in v2 of MD↔HTML loop.
- **Actionable items:**
  - [ ] src/devlead/serve.py — stdlib http.server based daemon, GET serves rendered HTML, POST accepts edits
  - [ ] HTML templates with `data-md-source="<file>"` attributes on editable regions
  - [ ] JS-light: minimal vanilla JS for inline edits, fetch POST on save
  - [ ] Validation: parsed MD must satisfy intake schema before write (reject on validation error)
  - [ ] Audit log every edit-from-HTML with editor identity, file, change summary
  - [ ] CLI: `devlead serve [--port 7777]` starts the daemon
  - [ ] Verify: edit FEATURES-0024 status from "pending" to "in_progress" via HTML, observe MD file updated and audit event written
- **Proposed BO:** (MD↔HTML loop, edit-back v2)
- **Proposed weight:** 0.10
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0030 - HTML form widgets per MD file type
- **Source:** Nitin direction 2026-04-17 (depends on FEATURES-0029)
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** Once `devlead serve` exists (FEATURES-0029), each MD-file type needs purpose-built HTML form widgets — intake entries get a status dropdown plus actionable-items checkbox grid plus summary textarea; hierarchy gets a BO/TBO/TTO tree editor with weight inputs; living docs get a contenteditable rich text editor; scratchpad gets an append-only entry form. The widgets enforce schema before submission. Without this, `devlead serve` would just be a generic textarea; with it, users get the visual co-edit experience Nitin envisions.
- **Actionable items:**
  - [ ] Per-file-type HTML widget templates in render.py
  - [ ] Intake widget: status dropdown, actionable items as checkbox list, summary textarea
  - [ ] Hierarchy widget: tree view with inline editing plus weight validation (must sum 100)
  - [ ] Living-doc widget: contenteditable with markdown preview
  - [ ] Scratchpad widget: append-only form (never lose old entries)
  - [ ] Verify: each MD file type has a tailored editing surface
- **Proposed BO:** (MD↔HTML loop, polish)
- **Proposed weight:** 0.05
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0031 - `devlead defrag` — file housekeeping (archive, merge, prune)
- **Source:** scratchpad:2026-04-17-devlead-defrag-command-file-housekeeping (Nitin approved 2026-04-17)
- **Captured:** 2026-04-17T05:00:00Z
- **Summary:** As projects age, devlead_docs/ files grow large and noisy: _intake_features.md is now ~430 lines with mix of done + pending entries; _scratchpad.md is ~898 lines with auto-captured user prompts; _audit_log.jsonl is ~2,200+ lines and growing. `devlead defrag` runs five housekeeping operations: (1) archive done intake entries to _intake_archive_*.md after 30-day grace period, (2) merge fragmented scratchpad entries by topic, (3) collapse repetitive audit-log runs (e.g. 50 consecutive gate_pass on same file → 1 rolled-up entry), (4) prune stale aware-file entries for deleted modules, (5) truncate state/effort/promise logs older than configurable window. Always hash-checked + reversible per the migrate.py pattern. Lower priority than MD↔HTML loop and BO-4 — schedule when files actually start hurting.
- **Actionable items:**
  - [ ] src/devlead/defrag.py — five operations as separate functions
  - [ ] Each operation outputs a dry-run plan first; user confirms before writes
  - [ ] Use migrate.py pattern: hash-check destination before removing source
  - [ ] CLI: `devlead defrag [--dry-run] [--scope intake|scratchpad|audit|aware|logs|all]`
  - [ ] Audit log every defrag operation with what was archived/merged/pruned
  - [ ] Tests for each operation independently + integration test on synthetic large files
  - [ ] Verify: `devlead defrag --dry-run` on this repo prints a sensible plan; full run shrinks _intake_features.md by 50%+ when the done entries reach 30-day archive eligibility
- **Proposed BO:** (operational hygiene, scales with project age)
- **Proposed weight:** 0.04
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0032 - Engagement-first HTML views — 4 emotional registers + glossary modal (gap-audited)
- **Source:** Nitin direction 2026-04-17 — "deep analytical skills, not sloppy. Keeping user engaged and excited and motivated is the name of the game" + "I dont like logical gaps"
- **Captured:** 2026-04-17T05:05:00Z (revised 2026-04-17T05:20:00Z to engagement framing + gap-audit)
- **Summary:** Engagement-first rendering, gap-audited so every active MD file has a home and every common user task has a workflow. Four pages, each answers ONE motivational question. Plus a glossary modal in nav. 5 explicit MD-file exemptions (LLM-only or archival) documented so nothing slips silently.
- **The four pages — each serves one motivational register:**
  1. **`now.html` — "Where I am"** *(confidence + clarity, daily-driver)*. Sources: `_resume.md` current focus + `_intake_features.md` in_progress/done + `_project_status.md` + recent `_intake_bugs.md` filings + (later) `_aware_status.md` recent slice. ONE recommended next move + alternatives. Concrete numbers in user-facing terms (LOC shipped, tests passing, first real C(τ) computed).
  2. **`vision.html` — "Why I'm doing this"** *(purpose, the motivation page)*. Sources: `_living_pitch.md` + `_living_vision.md` + `_living_goals.md` + `_living_project.md` + `_living_metrics.md` + `_project_hierarchy.md` BO data + `_living_decisions.md` (story so far) + `_living_demos.md` (see-it-work section). **BO/TBO editing surface lives here when FEATURES-0029 ships** (per BO↔TBO-is-human-owned principle). Per-BO drill-down to TBOs/TTOs available but de-emphasized (TBO→TTO is model territory).
  3. **`truth.html` — "Is this real?"** *(trust, the integrity page)*. Sources: `_living_buyer.md` (when extracted) + `_living_risks.md` + `_living_design.md` (current architecture) + `_living_technical.md` (how it actually works) + `_aware_features.md` (capability inventory) + `_aware_design.md` (module inventory) + `_project_hierarchy.md` convergence math derivation + audit-log evidence trail. Brutal-honest tables with ✓/⚠️/✗, no decorative happy-talk. Vapor list of features promised but not built — explicitly named.
  4. **`backlog.html` — "What else could I do?"** *(menu, secondary)*. Sources: `_intake_features.md` pending curated (FEATURES-NNNN only, sorted newest-first) + `_intake_bugs.md` open bugs (separate sub-section) + `_scratchpad.md` raw ideas (with promote-to-intake action when daemon ships) + `_intake_hierarchy_*.md` collapsed sub-section (auto-derived noise). Each entry: one-line value + effort estimate + dependencies + "set focus" button (when daemon ships).
- **Glossary access:** `_living_glossary.md` rendered as a `?` icon modal in nav, accessible from every page. Not a top-level page — terminology lookup is incidental, not a destination.
- **Explicit MD exemptions (no orphans):** `_routing_table.md`, `_living_standing_instructions.md` are LLM-facing infrastructure embedded in CLAUDE.md, not user-facing. `_resume_archive_*.md`, `_design_section1.md`, `interview_template.md`, `_intake_templates/*.tmpl` are archival/template, not active content. **All 5 exemptions justified inline; no MD file silently omitted.**
- **Logical-gap closure (vs prior 6-page draft):** bugs were missing → now in `now.html` (recent) + `backlog.html` (open). Glossary missing → now in nav modal. Aware files orphaned → now in `truth.html` capability/module inventory. Design + technical docs orphaned → now in `truth.html` architecture sub-sections. Scratchpad invisible → now in `backlog.html` raw-ideas. TBO/TTO drill-down hidden → now in `vision.html` per-BO drill-down. Demos file orphaned → now in `vision.html` see-it-work.
- **Why fewer pages beats more pages:** 6 pages = friction. 4 pages = obvious flow (`now` → `vision` for purpose → `backlog` to pick → execute → check `truth` if doubt). Glossary modal is incidental, not a destination.
- **Actionable items:**
  - [ ] render.py: `render_now_view()` aggregator with bug-recency, recent shipped, focused next-action card
  - [ ] render.py: `render_vision_view()` with BO progress bars, story-so-far timeline, per-BO TBO/TTO drill-down (collapsible)
  - [ ] render.py: `render_truth_view()` with vapor list, math derivation display, capability inventory, architecture
  - [ ] render.py: `render_backlog_view()` with curated FEATURES + open bugs + raw scratchpad ideas + collapsed hierarchy-derived
  - [ ] render.py: `render_glossary_modal()` returns HTML fragment for nav `?` icon
  - [ ] render.py: shared nav component with the `?` icon and inter-page links
  - [ ] Index page (`docs/views/index.html`) with 4 question-labelled entry cards + glossary access
  - [ ] Refactor `render_dir` to emit 4 register views + index; per-file HTMLs become opt-in (`--backing` flag)
  - [ ] Tests per aggregator + integration that opening `now.html` answers "where am I" in 5 seconds of reading
  - [ ] Coverage assertion: every active MD file appears in at least one rendered view OR has documented exemption
  - [ ] Verify: each of 4 pages reads like a coherent emotional answer, not a status dump
- **Proposed BO:** (MD↔HTML loop, engagement layer — supersedes prior task-oriented framing)
- **Proposed weight:** 0.08
- **Status:** pending
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)

## FEATURES-0028 ADDENDUM — BO↔TBO is human-owned, TBO→TTO is model-owned
- **Source:** Nitin direction 2026-04-17 — "BO↔TBO is owned by human, so you have to make it as visually appealing as possible. TBO→TTO is purely Model's expertise"
- **Captured:** 2026-04-17T05:05:00Z (clarification of FEATURES-0028)
- **Summary:** Key UX-investment principle for the rendering layer. The MD↔HTML loop should invest **heavily** in BO↔TBO views (visually appealing, editable, prioritisation-friendly — humans set strategy here) and **minimally** in TBO→TTO views (compact, mostly read-only, math-driven — models compute here). When FEATURES-0028 (rich intake/hierarchy views) and FEATURES-0029 (`devlead serve` edit-back) ship, the editable surface should be: BO weights, BO metrics/baselines/targets, TBO descriptions, TBO ordering. NOT: TTO `verify:` commands, TTO `intent_vector` floats, TTO weight ints (those flow from math + LLM judgment). This insight makes FEATURES-0032 view #3 ("Vision & BOs") the highest-investment page.
- **Action:** absorb into FEATURES-0028 design when that work begins; do not ship as standalone.
- **Status:** captured
- **Origin:** normal

## FEATURES-0033 - Cross-cutting design constraint: absorb complexity, expose simplicity
- **Source:** Nitin direction 2026-04-17 — "whole game is outsourcing complexity to Claude (DevLead) and presenting simple, elegant and clean picture to user. No clutter, no noise"
- **Captured:** 2026-04-17T05:25:00Z
- **Summary:** Not a feature to ship — a **design constraint that gates every other feature**. The shipped product is currently a power-user toolkit (15+ CLI commands, 23 MD files, Greek letters in dashboard, BO/TBO/TTO acronyms in user-facing surfaces, intake-file knowledge required for actions). The principle: DevLead/Claude absorbs complexity; user sees simple, elegant, clean. Every PR / FEATURES entry from now on must pass the filter: "does this absorb complexity or expose it?" If exposing, redesign or split the surface (power-user CLI vs simple-user UI).
- **Audit of current complexity leaks (FEATURES-0033 informs how to fix each):**
  - CLI verb soup: 15+ commands user must remember → one web entry, CLI as power-user fallback
  - Intake file knowledge: user types `--into _intake_features.md` → auto-infer from content
  - FEATURES-NNNN IDs: hand-allocated → auto-named from content keyword
  - BO/TBO/TTO acronyms: "enterprise theatre" per Tab 3 → plain English in HTML (goal/theme/task); MD keeps acronyms for LLM
  - Greek letters in dashboard: α/φ/ε/G → plain labels (alignment/delivery/efficiency/gravity)
  - MD file type distinctions: `_intake_*` vs `_living_*` vs `_aware_*` → semantic sections in HTML, user never types filename
  - `_resume.md` raw markdown: → one page "Here's where you are, click to continue"
  - Status lifecycle: `pending → in_progress → done` → "Start" / "Mark done" buttons
  - Multiple in_progress entries: gate cwi shows confusing multiples → UI shows single focus, expandable
  - Convergence math derivation: formulas → "C = 3.1% because BO-001 is 3% of the way" with "tap for math" link
  - Audit-log JSONL: → "Recent activity" cards in plain English
  - Dashboard 11 tabs: file-type leakage → 4 emotional-register pages (FEATURES-0032, already addressing)
- **Actionable items (none individually — this is meta):**
  - [ ] Every new FEATURES entry from now must include a "complexity audit" line: what does this absorb, what does it expose?
  - [ ] Existing FEATURES-0024 onwards review: where does each leak complexity? Update intake entries with mitigation notes.
  - [ ] FEATURES-0032 (engagement views) explicitly inherits this constraint: NO acronyms in HTML, NO Greek letters, NO file paths shown to user
  - [ ] Consider FEATURES-0034: rename CLI commands or hide them behind a single `devlead` interactive entry point
  - [ ] Consider FEATURES-0035: HTML view word-mapping layer (BO → "goal", α → "alignment", etc.) — applied at render time, MD stays canonical
- **Nature:** **Cross-cutting design principle** — applies to every FEATURES entry from this point forward. Not implemented as code; lived as a discipline.
- **Proposed BO:** (UX foundation, all subsequent work)
- **Proposed weight:** N/A (constraint, not deliverable)
- **Status:** active-principle
- **Origin:** normal
- **Promoted to:** (pending)
- **Promoted at:** (pending)
