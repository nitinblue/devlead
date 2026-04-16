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
- **Status:** pending
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
