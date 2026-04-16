# DevLead v2 — Session Resume (`_resume.md`) — the project's scratchpad / triage inbox

> **This file always exists.** It is the project's **scratchpad** — a fast-capture space for anything the user has said that doesn't yet have a dedicated home. Mentally, think of it as a **triage inbox**: items sit here until they find the right file to live in, then they get migrated out. The scratchpad does not retire, does not disappear, does not empty out permanently — but its goal is to be **as lean as possible**. The leaner `_resume.md` is, the better the project has triaged into dedicated files.
>
> **No history.** `_resume.md` contains only currently-untriaged items + resume context for the next session. It does NOT contain session logs, completed work records, or archived decisions. History lives in dedicated files (`_audit_log.jsonl`, `_migration_log.jsonl`, design docs) or in git.
>
> **Session protocol.**
> - **At session start:** Claude reads `devlead_docs/_resume.md` first, before anything else. Always. It's the catch-up pointer.
> - **During session:** Claude triages aggressively. Whenever an item in `_resume.md` finds a proper home (a dedicated file that can carry it), Claude migrates it out (hash-verified, audited — see zero-loss rule below).
> - **Before session exit:** Claude must write any new untriaged items to `_resume.md`. If the user said something important during the session that doesn't yet have a dedicated file, it gets captured here so it's not lost.
>
> **Zero information loss is a hard guarantee.** Nothing leaves this file unless the destination verifiably holds the same content. Migration is audited, hash-checked, reversible, and hard-blocked (exit 2) if the destination is missing. This is the ONE rule in DevLead that enforces hard even in warn-only mode — information loss is unrecoverable and cannot be a warning.
>
> **Filename: `devlead_docs/_resume.md`** — short, memorable. Say "check the resume" and it's unmistakable.

---

## 0. What to do first, in order

1. Read this file in full (you are doing that now).
2. Read `devlead_docs/_design_section1.md` — Section 1 of the DevLead design is already locked on disk.
3. Read `src/devlead/scaffold/interview_template.md` — the 5-block interview playbook.
4. Skim memory files: `project_devlead_v2_redesign.md`, `feedback_no_adjacent_invention.md`, `feedback_enforcement_posture.md`, `user_nitin.md`.
5. Jump to Section 14 of this file ("Where to resume exactly") and start there.

Do NOT read or mine anything in `legacy/v1/` unless Nitin explicitly points there — that's v1's archive and it is off-limits by rule.

---

## 1. What DevLead is (the pitch)

DevLead is a **governance layer installed as a Claude Code plugin** on any software project. It sits between the human engineer and the AI coding assistant and enforces one rule: **all work originates from a single canonical store, and all results go back to that store.** Nothing the AI does happens outside that loop. LLM memory is a derived view of the store — never an independent source.

**Core function:** take a high-level requirement of a software project, convert business objectives into technical deliverables, do it with the least wasted time, effort, and tokens.

**What a traditional (human) Dev Lead does:** keeps technical implementation converging toward business objectives; sees drift; re-prioritizes; kills shadow work; runs retros; pivots when reality diverges. DevLead-the-product **replicates that accountability continuously, mathematically, and visibly.** It is not a task tracker. It is a convergence engine with enforcement and transparency built in.

**Target user:** solo engineers and small teams using AI aggressively who need to stay in the driver's seat. Secondary: anyone building a non-trivial project who wants AI assistance without giving up ownership of direction.

**Why it wins:** every other AI dev tool optimizes for *speed*. DevLead optimizes for *control*. You can read one directory and know everything the AI knows about your project.

---

## 2. Top-most goal (Nitin's own words, 2026-04-12)

> "Nitin wants to develop a Claude Plugin called DevLead. Devlead as name suggests is capable of taking a high level requirement of a software project, is able to convert business objectives into technical deliverables, does it with least wastage of time, effort, token — Nitin wants to start generating revenue selling this plugin — first revenue should come in a weeks time, $1000 in 1 month after first revenue."

**Revised dates** (after Nitin's no-corner-cutting directive — full-feature v1 over cut MVP):
- **First revenue target: 2026-05-08** (27 days from Apr 12)
- **$1000 cumulative target: 2026-06-08** (one month after launch)

These dates slipped from the original "1 week / 1 month" because Nitin chose full-feature over a thin MVP. That's the trade.

---

## 3. Locked design decisions (do not re-open unless Nitin asks)

| Decision | Value |
|---|---|
| Form factor | Claude Code plugin; repo root IS the plugin root |
| Distribution | Open-core on public GitHub + paid features in private `devlead-pro` package |
| License (core) | MIT |
| License (paid) | Commercial |
| Hierarchy | `Vision → Goals → Phase → BO → TBO → TTO` |
| Story layer | **KILLED** — use TBO for user-visible, TTO for technical-atomic |
| Task renamed | `Task → TTO` (Tangible Technical Objective) |
| Goals | First-class, target-dated, linked to BO subsets, parallel to Vision |
| State machine | **KILLED** — `_project_status.md` uses flags derived from other files, no states |
| Enforcement posture | **Warn by default** (exit 0 + systemMessage); block only in opt-in strict mode |
| Exit codes | **Nothing in v2 ever exits 2** unless strict mode is explicitly enabled |
| NFR handling | **Shape A** — NFRs as tagged TTOs under the same parent TBO as functional TTOs, sharing convergence rollup |
| Config | Two layers — `.claude/settings.json` (plumbing) + `devlead.toml` (user rules) |
| KPIs at launch | 5 of 9: K1 Convergence, K5 Tokenomics, K7 Drift, K8 Goal Yield, K9 Word-Keeping |
| Pricing | Free (1 project), $29/yr (5), $49/yr (unlimited), $99 lifetime |
| Payment processor | Lemon Squeezy (handles tax, webhooks, license keys) |
| License server | Cloudflare Worker + D1 (free tier) |
| Price justification | Full feature set — all 4 hooks, 5 KPIs, goals, commitments, convergence, enforcement |
| Plugin integration | **Zero disruption** — DevLead never modifies other plugins' flows, file paths, or defaults (added 2026-04-14) |
| Single source of truth | All work traces to `devlead_docs/`; plugins feed in via `_intake_*.md` files, never by modification (added 2026-04-14) |
| Dark code | **Forbidden** — any code whose origin doesn't trace intake → TTO → TBO → BO is detectable; warn in v1, optional block in v1.1 (added 2026-04-14) |
| Hierarchy (revised 2026-04-14) | `Sprint -> BO -> TBO -> TTO`. Vision killed. **BO = Goal** (merged): BOs are now goals with target dates; no separate Goals layer. K8 "Goal Yield" -> K8 "BO Yield". |
| Top container name | **Sprint**. DevLead's Sprint is scoped to ship-windows / versions (months), NOT the agile 2-week cadence. Docs must be explicit to avoid confusion. |
| File recognition by prefix | DevLead globs `_intake_*.md`, `_living_*.md`, `_project_*.md` — treats every match as the corresponding type. Users create as many files per category as they want with any slug. Install ships starter templates only; taxonomy is open. |
| Intake ID scheme | Derived from filename slug, uppercased: `_intake_features.md` -> `FEATURES-NNNN`, `_intake_security_findings.md` -> `SECURITY-FINDINGS-NNNN`. No hardcoded prefix constants. |
| Intake schema | **Template-driven, not free-form.** Onus is on Claude/LLM to fill fields; template constrains what fields exist. Templates live in `devlead_docs/_intake_templates/*.md` as real editable files. **v1 ships ONE template (`default.md`); all intake files use it.** Users pick from multiple templates as more are added in v1.1+. Auto-update from user behavior is v1.1. |
| Intake capture effort | Lean: Claude drafts every field at ingest (title, summary, actionable items, proposed BO/Sprint/weight). User only confirms or corrects placement hints at triage. |
| Self-Awareness framework | DevLead maintains `devlead_docs/_aware_*.md` files - code-derived, auto-generated descriptions of the current state of the project (features, design, later: metrics, deps, invariants). LLM reads them at session start AFTER `_resume.md` and `_scratchpad.md`. **Structured memory substrate; reduces reliance on `CLAUDE.md` alone.** v1 ships `_aware_features.md` + `_aware_design.md` via `/devlead awareness`; v1.1 adds more aspects and auto-refresh on Stop hook. Hand-edits are overwritten - files are derived, not authored. |
| `_aware_*` vs `_living_*` | `_living_*.md` = curated intent (design goals, decisions, glossary). `_aware_*.md` = observed reality (what the code actually does right now). Both exist; don't conflate them. |
| Dev work discipline | **Hard rule:** every code change must trace to an entry in `_intake_*.md`. Bugs Claude finds mid-task force a STOP -> scratchpad note -> `/devlead ingest --from-scratchpad <needle> --into _intake_bugs.md` -> fix. No inline "quick cleanups" outside the intake flow. Rule lives in `CLAUDE.md`. Enforcement is advisory in v1 (warnings); v1.1+ adds hook-based blocks. |
| Scratchpad -> intake conversion | `/devlead ingest --from-scratchpad <needle> --into <_intake_file.md>` converts a scratchpad entry directly into an intake entry (no plugin plan required for well-scoped items). Bidirectional trace: intake source is `scratchpad:<entry-id>`; the scratchpad entry gets a `> **Promoted:**` cross-reference line in its body. |
| Actionable-items floor | Every intake entry must have >=1 actionable item. Zero-item entries trigger a warning at ingest: "every TBO must map to granular TTOs - refine or reject before promoting". |
| Forced-work procedure | When user dictates work outside normal flow: Claude (1) STOPS, (2) creates intake entry FIRST with best-effort BO/TBO/TTO association, (3) marks it `--forced` so `origin="forced"`, (4) THEN does the work. CLAUDE.md enforces; advisory in v1. This keeps trace integrity even under pressure. |
| K_BYPASS KPI (v1.1 placeholder) | Future KPI: fraction of intake entries with `origin == "forced"`. High value = discipline slipping under user pressure. [T] transparency, [P] pivot trigger. v1 ships the `origin` field; v1.1 wires the calculation alongside K1/K5/K7/K8/K9. |
| Config format — YAML approved | User approved YAML as a valid format for future config files (`devlead.yml` etc). TOML from the original design is still acceptable; both are allowed. Decide per-file when the config layer ships (Week 2). |

---

## 4. The hierarchy (with math)

```
Vision                   (aspirational end state)
  │
  ├── Goals              (target-dated aspirations — first-class objects)
  │     └── linked subset of BOs (one goal can span multiple BOs)
  │
  └── Phase              (delivery phase: MVP, GA, v2, ...)
        └── BO           (Business Objective — measurable outcome, weighted)
              └── TBO    (Tangible Business Outcome — "user can now do X")
                    └── TTO (Tangible Technical Objective — atomic technical work)
```

**Weights.** Every non-root node has `weight ∈ [0, 100]`. Sibling weights **sum to 100 within their parent**: Phases under Vision → 100; BOs under Phase → 100; TBOs under BO → 100; TTOs under TBO → 100.

**Base completion.** `tto.completion ∈ [0, 100]` — reported by engineer or inferred from commits/tests. Only hand-typed signal.

**Rollup formula** (recursive, from leaves up):
```
convergence(node) = Σ over children c:  (c.weight / 100) × convergence(c)
```

**Example.** BO has two TBOs with weights 60 and 40. TBO-1 rolls up to 80%. TBO-2 rolls up to 30%. BO convergence = `0.60 × 80 + 0.40 × 30 = 60`.

**Goal convergence.** A Goal's linked BO subset is rolled up independently — gives a per-goal scalar. `_living_goals.md` tracks each goal's convergence separately from the Phase/Vision rollup.

---

## 5. The 9 KPIs (5 ship in v1, 4 in v1.1)

Each tagged **[E]** enforce, **[T]** transparency, **[P]** pivot trigger.

| ID | Name | Role | Formula (short) | Launch? |
|---|---|---|---|---|
| K1 | Convergence | [T][P] | weighted rollup above | ✅ v1 |
| K2 | Going in Circles | [E][T] | `rework_edits / total_edits` | v1.1 |
| K3 | Skin in the Game | [E][T] | `user_validation_events / total_events` | v1.1 |
| K4 | Time Investment Divergence | [T][P] | per BO: `|effort_share − weight_share|` | v1.1 |
| K5 | Tokenomics | [T][P] | per BO: `tokens_spent / Δ_convergence` | ✅ v1 |
| K6 | Shadow Work | [E][T] | `actions_without_task_linkage / total_actions` | v1.1 |
| K7 | Drift | [E][T] | per-prompt topic match vs top-priority TTO, window avg | ✅ v1 |
| K8 | Goal Yield | [T][P] | `goals_achieved_on_time / goals_committed` | ✅ v1 |
| K9 | Word-Keeping Ratio | [E][T] | `commitments_kept_on_time / commitments_made` | ✅ v1 |

K9 is **the killer feature** — it makes Claude accountable for every promise it makes across sessions. Every time Claude says "I'll ship X by Day N", it should call `/devlead commit ... --by DATE`. At target date, Claude must resolve with `/devlead resolve <id> kept|broken`. K9 is the public scorecard.

---

## 6. The 7 architectural layers

```
USER (human) → 1. CAPTURE (interview, intake) → 2. STORE (devlead_docs/) →
  │
  ├→ 3. PROJECTION (LLM memory sync)
  └→ 4. GOVERNANCE (gates, ordering, drift detection)
                │
                └→ 5. CONVERGENCE ENGINE (rollup + K1-K9) → 6. VISIBILITY (CLI/dashboard)
                                                               → 7. AUDIT (jsonl + Promise Ledger)
                                                                      ↑
                                                                      │ hooks
                                                                  LLM (Claude)
```

Hooks: `SessionStart`, `UserPromptSubmit`, `PreToolUse` (Edit|Write), `Stop`. All four fire during v1. **Currently not registered** — v1's hooks were cleared from `.claude/settings.json` during Session 2 to stop accidental blocks. v2 hooks register when the gate engine ships in Week 2.

---

## 7. Pricing and open-core split

### Free / open-source core (MIT, public GitHub)
- `/devlead init`, full scaffolding, all 4 hooks
- `/devlead interview` (5 blocks, full template)
- `/devlead status` (text output)
- BO/TBO/TTO hierarchy + weighted rollup
- K1, K5, K7 (three KPIs)
- Audit log, warn-mode enforcement
- 1-project limit (counted in `~/.devlead/projects.json`)

### Paid (`devlead-pro` private package, installed on license activation)
- `/devlead goal` + K8 + at-risk detection
- `/devlead commit` + `/devlead resolve` + K9 + Promise Ledger
- `/devlead pivot` full repivot ceremony
- KPIs K2, K3, K4, K6 (v1.1)
- Block-mode strict enforcement
- HTML dashboard (v1.1)
- Up to 5 projects (Personal) / unlimited (Pro, Lifetime)
- Priority support

### License architecture
- **Payment:** Lemon Squeezy
- **License server:** Cloudflare Worker + D1 SQLite (free tier, ~$0/mo)
- **Activation:** `/devlead license activate <KEY>` calls server's `/verify`; result cached in `~/.devlead/license.json` with weekly re-ping; 30-day offline grace then tier downgrades gracefully.
- **Paid-code delivery:** on activation, plugin downloads `devlead-pro` from private PyPI. The open-core repo does not contain paid code — nothing to patch out.

### Revenue math to $1000
Mixed distribution: 3 × Lifetime ($297) + 15 × Personal ($435) + 6 × Pro ($294) = **$1026** in month 1 post-launch.

---

## 8. Config surface (two layers)

### Layer 1 — `.claude/settings.json` (DevLead-owned plumbing)
Routes each hook event to `devlead gate <event>`. Written automatically by `/devlead init`. Users do not edit.
```json
{ "hooks": { "SessionStart": [{"hooks":[{"type":"command","command":"devlead gate SessionStart","timeout":10}]}], "UserPromptSubmit": [...], "PreToolUse": [{"matcher":"Edit|Write","hooks":[...]}], "Stop": [...] } }
```

### Layer 2 — `devlead.toml` at project root (user-owned)
Plain TOML. Sections: `[enforcement]` (mode: warn|block, global), `[[enforcement.rules]]` (per-rule event/matcher/check/action/message), `[kpis]` (thresholds), `[interview]` (block order, lock requirements), `[goals]` (at-risk window 20%, convergence threshold 0.5).

**Defaults at install:** `enforcement.mode = "warn"`, all rules enabled, K7 threshold 0.5, K8/K9 warn at 0.7, interview blocks ordered A→B→C→D→E, lock required.

---

## 9. Current build state (end of Session 2, 2026-04-12)

### Files on disk and verified working

| Path | What it is |
|---|---|
| `.claude-plugin/plugin.json` | Plugin manifest, v0.2.0-dev, MIT |
| `commands/init.md` | `/devlead init` slash command |
| `src/devlead/__init__.py` | `__version__ = "0.2.0-dev"` |
| `src/devlead/__main__.py` | Entry point, delegates to `cli.main` |
| `src/devlead/cli.py` | Subcommand dispatch. `init` works. Unknown commands exit 0. |
| `src/devlead/install.py` | Install logic + `InstallReport` class. Idempotent. |
| `src/devlead/scaffold/*.md.tmpl` (10 files) | All scaffold templates |
| `src/devlead/scaffold/interview_template.md` | Full 5-block interview playbook with Phase 0 inspection, propose-first flow, 10-15 min target, NFR Shape A example |
| `devlead_docs/_design_section1.md` | Section 1 of DevLead's own design, locked |
| `devlead_docs/_resume.md` | This file |
| `devlead_docs/_project_status.md` | Installed from scaffold, flags section (no state machine) |
| `devlead_docs/_project_hierarchy.md` | Installed, empty BO tree |
| `devlead_docs/_living_*.md` (8 files) | Installed, empty living docs |
| `devlead_docs/_audit_log.jsonl` | Installed, empty |
| `devlead_docs/_promise_ledger.jsonl` | Installed, empty |
| `devlead_docs/interview_template.md` | Copy of scaffold template, for in-project reference |
| `.claude/settings.json` | **Cleared** — `{"hooks": {}}`. v1 hooks removed. |
| `CLAUDE.md` | Rewritten for v2 |
| `README.md` | Rewritten for v2 |
| `legacy/v1/` | v1 archived untouched, git tag `v1-archive-2026-04-12` |

### Verified end-to-end
```
PYTHONPATH=src python -m devlead init /tmp/test-project   # 13 files created
PYTHONPATH=src python -m devlead init /tmp/test-project   # idempotent, 13 skipped
PYTHONPATH=src python -m devlead init .                   # dogfood, DevLead installed on its own repo
```

---

## 10. The 27-day build plan — current position

- ✅ **Day 1 (Apr 12):** Scope locked. Plan approved. Interview template v2 content written.
- ✅ **Day 2 (Apr 12):** Plugin skeleton + `/devlead init` + 10 scaffold templates + install logic + dogfood on DevLead's own repo.
- ⏳ **Day 3 (next session):** `/devlead interview` command.
- Day 4: Store layer — parsers/writers for BO/TBO/TTO, weight validation, schema enforcement.
- Day 5: Hook infrastructure — wire all 4 hooks end-to-end.
- Day 6: Gate engine — warn/block modes, rules DSL.
- Day 7: Week 1 buffer.
- Week 2 (Days 8-14): Convergence math, K1/K5/K7/K8/K9, goal tracking, commitment ledger, audit, projection, `/devlead status`, external dogfood.
- Week 3 (Days 15-20): NFR integration, repivot loop, DevLead-on-DevLead dogfood, polish.
- Week 4 (Days 21-24): Landing page, demo video, plugin marketplace submission, public launch, first revenue May 8.

---

## 11. Critical gotchas — do not repeat these

1. **Nothing exits 2 in v2 by default.** `src/devlead/cli.py` returns 0 on unknown commands. The one time I made it return 2, v1 hooks caused accidental hard blocks on every Edit/Write. Fixed; do not re-introduce.
2. **v1 hooks in `.claude/settings.json` are cleared.** `{"hooks": {}}` is the current state. v2 hooks register when the gate engine ships in Week 2, NOT before.
3. **State machine is dead.** Don't re-introduce `AWAITING_INTERVIEW` or any state transitions. `_project_status.md` has derived flags only.
4. **`legacy/v1/` is untouched and off-limits.** Don't mine it unless Nitin explicitly points at a specific file.
5. **Windows cp1252 console can't encode em-dash, arrows, or most Unicode.** Keep all `print()` output in `src/devlead/*.py` ASCII-safe.

---

## 12. Rules of engagement (hard-won this session, do not violate)

- **User dictates, Claude captures.** If Nitin hasn't said it, it doesn't exist.
- **Claude proposes only inside the layer Nitin named.** "Propose as much as you can" is scoped to that one layer. No silent invention of adjacent layers (files in devlead_docs/, CLAUDE.md rules, install flags, etc.).
- **Layer by layer, one at a time.** Finish what Nitin named before opening anything new. If you think a gap exists, name it in one sentence and wait.
- **Plan mode is the harness guardrail.** Re-enter plan mode during design phases. Stay in it until Nitin says "exit and build X."
- **Disagreements are surfaced loudly, not routed around.** If a new direction conflicts with something locked, say so in one sentence.
- **Multi-session is fine and expected.** No pushing to "finish" anything in one sitting.
- **The burden is on Claude to notice mid-response when it's about to jump and stop.** This is the single most important behavior Nitin is trying to get out of you.
- **Do not write to any file without Nitin's explicit approval.** Even plan files, even scratch files. The whole point of DevLead is that nothing happens outside the loop.

---

## 13. Open threads (explicitly undecided, surface when relevant)

- **Exact `commands/interview.md` flow** — to be designed on Day 3 (next session).
- **Store layer markdown schema** — how BO/TBO/TTO serialize (plain headers vs YAML frontmatter). Decide on Day 4.
- **NFR default catalogs per project type** — web service, CLI, library, mobile app, data pipeline. Decide when Block D support lands.
- **License server implementation details** — Cloudflare Worker boilerplate. Defer to Week 3.
- **Goal at-risk thresholds** — at-risk window 20% of target date, convergence threshold 0.5. Validate during dogfood.
- **First-customer candidate** — Nitin needs a warm list of 3 by May 3 for direct-sales push on launch day.
- **Landing page copy ownership** — Nitin writes, or Claude drafts and Nitin edits.
- **Exact set of `_intake_*.md` files** — Nitin named `_intake_features.md` and `_intake_bug_issues.md` (2026-04-14). v1 had more (bugs, changes, features, gaps). Finalize in plan mode (Section 20).
- **Intake file schema** — markdown sections vs YAML frontmatter vs table rows. Must be parseable by DevLead and readable by humans. Decide in plan mode.
- **Intake → hierarchy promotion** — manual command, triage session, or auto-promote on backlog load? Decide in plan mode.
- **Plugin output → intake handoff mechanism** — explicit `/devlead ingest <path>`, Stop-hook watcher, or Claude-driven after every plugin flow? Decide in plan mode.
- **Section 18 conflation (stale)** — Section 18 defines `_resume.md` AS the scratchpad, but Nitin split them on 2026-04-14 (`_scratchpad.md` is now the raw capture file, `_resume.md` is the handoff memory file). Section 18 needs rewrite to reflect this split. Do not touch until a design section locks the new two-file split semantics.
- **Section 4 stale hierarchy diagram** — Section 4 still shows `Vision -> Goals -> Phase -> BO -> TBO -> TTO`. New hierarchy is `Sprint -> BO -> TBO -> TTO` (Vision killed, BO=Goal merged). Section 4 must be rewritten. Do not touch until the new hierarchy math is locked in a design section.
- **`_living_goals.md` redundancy** — Now that BO = Goal, the `_living_goals.md` scaffold file is largely a view over the BO section of `_project_hierarchy.md`. Options: (a) repurpose it as a derived view, (b) remove it from the scaffold, (c) keep as alias. Decide on Day 4 when the store layer ships.
- **Template auto-update loop** — Intake templates should evolve from user behavior (fields always left blank, fields user adds manually, wording changes). v1 ships static templates; the watch-and-propose loop is v1.1. Deferred.
- **Template versioning** — When a template changes, how do existing entries written against the old template get read/rendered? Needs a version field on each template file + a migration story. Decide before v1.1 template-update loop.
- **Sprint-vs-agile naming collision** — DevLead's Sprint is months/versions, not agile 2-week. Users from agile backgrounds will assume the shorter cadence. Mitigate with docs; monitor for confusion reports during dogfood. If pushback is high, revisit naming.

---

## 14. Where to resume exactly (next session's first action)

> **2026-04-14 update:** The Day 3 deliverable below is being re-derived in light of **Section 20 (Plugin Bridge + Intake Flow)**. The original `/devlead interview` framing is not wrong — it becomes the first *consumer* of the plugin bridge rather than its own bespoke pipeline. Concrete Day 3 steps will be overwritten once the plan-mode output is approved.

**Day 3 deliverable: build the `/devlead interview` command.**

This is the command that drives the 5-block interview per `src/devlead/scaffold/interview_template.md`. It must:

1. Perform **Phase 0 inspection** on the current project (read README, package manifests, file tree, git log, existing docs) — all read-only, under 60 seconds of LLM work. Build an internal project profile.
2. For each of Blocks A–E, follow the **propose-first** pattern: Claude drafts content from Phase 0 profile + prior block answers, presents as a draft, asks 1-3 anchor questions only when necessary, user corrects, Claude locks the block.
3. Capture outputs to the correct files: Block A → `_living_project.md`, Block B → `_project_hierarchy.md` + `_living_goals.md` + `_living_metrics.md`, Block C → `_living_technical.md`, Block D → `_living_design.md` (+ NFR TTOs in `_project_hierarchy.md`), Block E → `_living_glossary.md` + `_living_standing_instructions.md` + `_living_risks.md`.
4. Support resume-from-mid-block via `_project_status.md` flags (not states).
5. **Target: under 15 minutes active user time for a typical project.**

**Concrete Day 3 steps, in order:**

1. Write `commands/interview.md` — the slash command file with instructions to Claude on how to conduct the interview. It reads the scaffold template at `src/devlead/scaffold/interview_template.md` as the source of truth for block content.
2. Write `src/devlead/interview.py` — small Python helper module with pure functions for Phase 0 inspection (read README, parse `pyproject.toml`, list file tree, get git log summary, detect project type). No LLM calls in Python.
3. Write `src/devlead/store.py` — parsers and writers for BO/TBO/TTO in markdown format. Decides the schema (likely: headers for structure, inline `(weight: N)` annotations, `[type: non-functional]` tag for NFRs). Keep it dead simple — no YAML frontmatter unless forced.
4. Wire `cli.py` to expose `devlead interview` and `devlead inspect` subcommands.
5. **Dogfood immediately:** run `/devlead interview` on DevLead's own repo, using Section 1 + the architectural brief as the source material. Capture Nitin's actual answers into `devlead_docs/_living_*.md`. This is the first real use of the feature.

**Do not do:**
- Do not build the gate engine yet (Day 6).
- Do not add hooks yet (Day 5).
- Do not touch `.claude/settings.json` — it stays `{"hooks": {}}` until gate engine ships.
- Do not introduce state machines anywhere.
- Do not change the hierarchy or KPI list — they're locked.
- Do not invent adjacent-layer scope (commitment ledger is Day 11, not Day 3).

---

## 15. Key file references

| What | Where |
|---|---|
| This resume file | `devlead_docs/_resume.md` |
| Section 1 design (locked) | `devlead_docs/_design_section1.md` |
| Interview template (5-block playbook) | `src/devlead/scaffold/interview_template.md` |
| Plan file (harness-owned backup) | `C:\Users\nitin\.claude\plans\shimmying-hatching-parasol.md` |
| Install logic | `src/devlead/install.py` |
| CLI dispatch | `src/devlead/cli.py` |
| Plugin manifest | `.claude-plugin/plugin.json` |
| Init slash command | `commands/init.md` |
| v1 archive (off-limits) | `legacy/v1/` |
| v1 git tag | `v1-archive-2026-04-12` |

---

## 16. Memory files to read at session start

- `project_devlead_v2_redesign.md` — current project state snapshot
- `feedback_no_adjacent_invention.md` — hard-won interaction pattern (do not invent adjacent layers)
- `feedback_enforcement_posture.md` — warn-only enforcement preference
- `user_nitin.md` — Nitin's profile and working style
- `feedback_file_size.md` — keep files small
- `feedback_subagent_mode.md` — subagent-driven execution default

---

## 17. Housekeeping — when this file needs maintenance

- After every session, update Section 10 (where we are in the 27-day plan) and Section 9 (current build state).
- When a design decision changes, update Section 3.
- When a gotcha is discovered, add it to Section 11.
- When an open thread is resolved, remove it from Section 13 and add the resolution to Section 3 or wherever it belongs.
- When a section here matures into a dedicated file, **migrate it** (see Section 18 below for the migration protocol — do not just delete).

---

## 18. Session Resume — a first-class DevLead v1 feature

> **Captured 2026-04-12 (Session 2).** Nitin dictated this as a must-have feature: *"Can this be a feature in DevLead, start of project, DevLead starts with a massive file, and keeps trimming it down as makes progress, and report burndown chart on this... nothing more frustrating for user if any information lost from initial sessions."* And clarified: *"_resume will always exist, but leaner the better, it will not contain any history, but claude should know which file to write before exiting, and to read this file at the start of session... this is same as triaging, any work that has not been triaged will need to stay here, till the line item finds proper home... scratchpad kind of file."* This section is the feature spec.

### 18.1 Concept

`_resume.md` is the project's **scratchpad / triage inbox**. It is a fast-capture space where any item that doesn't yet have a proper home lives until it finds one. It is **always present** — it does not retire, does not empty out, does not disappear. It **starts empty**, grows when sessions dump untriaged items, and shrinks when items get migrated to their dedicated homes.

**Three things live in `_resume.md`:**
1. **Untriaged items** — anything the user has said that doesn't yet have a dedicated file. A raw intake bucket.
2. **Resume pointers** — short cross-references to where locked content has moved (so the next session can navigate: "Section 4 was migrated to `_living_project.md`").
3. **Session handoff notes** — the "where we are right now" cursor: what's in progress, what's next, what's blocked.

**Four things do NOT live in `_resume.md`:**
- Session logs or audit history — those live in `_audit_log.jsonl`.
- Completed design decisions — those migrate to `_design_*.md` files.
- Long architecture content — migrates to `_living_technical.md` / `_living_design.md`.
- Permanent project instructions — those belong in `CLAUDE.md`.

`/devlead init` creates `_resume.md` as an empty scratchpad with just a header template. It grows and shrinks continuously through the project lifetime. The goal is **always as lean as possible, but never empty** — there's always a session handoff note at minimum.

### 18.2 Session protocol (hard rule for Claude)

The protocol Claude must follow every session, enforced via `CLAUDE.md` instruction + `SessionStart` hook + `Stop` hook:

1. **At session start (SessionStart hook / CLAUDE.md rule):** Claude reads `devlead_docs/_resume.md` FIRST, before any other file. It contains the catch-up pointer and any untriaged items from prior sessions.
2. **During session:** Claude triages aggressively. Whenever an item in `_resume.md` finds a proper home, Claude migrates it out (hash-verified, audited — see 18.4). Triage is continuous, not end-of-session.
3. **Before session exit (Stop hook):** Claude must write any new untriaged items from THIS session to `_resume.md`. If the user mentioned something important that doesn't yet have a dedicated file, it gets captured here before Claude stops. Stop hook verifies this happened and warns if it didn't.

Missing either side of this protocol = information loss risk. The Stop hook enforcement is what prevents end-of-session amnesia.

### 18.3 Leanness phases (descriptive, not stages with transitions)

The file's size tells you roughly how triaged the project is. These are descriptive bands, not formal states:

| Lines | Band | What it means |
|---|---|---|
| > 1000 | **Fat** | Early in project OR triage is falling behind. Migrate aggressively. |
| 200–1000 | **Normal** | Healthy capture/triage rhythm, some backlog is expected. |
| < 200 | **Lean** | Most content lives in dedicated files; `_resume.md` is mostly handoff + a few untriaged items. |
| < 50 | **Minimal** | Near-ideal state: just session handoff + 1–3 items pending triage. |

**Nothing happens automatically based on these bands.** They're display labels. `/devlead status` shows the current band so you can see at a glance how much triage debt has accumulated.

### 18.4 Zero information loss — hard guarantee

**This is the one rule in DevLead that enforces hard, even in warn-only mode.** Information loss is unrecoverable, so warnings are insufficient.

The guarantee, stated plainly:
> Nothing is ever removed from `_resume.md` unless the destination file verifiably holds the same content. If the destination is missing, empty, or content-mismatched, the removal is blocked. Period.

Implementation:
1. Migration is proposed: *"Section 4 of `_resume.md` should move to `_living_project.md`."*
2. DevLead computes a content hash of the source section.
3. DevLead checks whether `_living_project.md` contains content matching that hash.
4. **If yes:** safe to remove from `_resume.md`. Append to `_migration_log.jsonl`. Remove.
5. **If no:** migration is blocked. DevLead says: *"Target `_living_project.md` does not contain this content. Write it to the target first, then retry the migration."*

This is the only place `exit 2` (hard block) is allowed in v2's default config.

### 18.5 Burndown tracking

Every time `_resume.md` is modified, DevLead appends a line to `devlead_docs/_resume_burndown.jsonl`:

```jsonl
{"timestamp":"2026-04-12T...", "lines":847, "delta":-12, "session_id":"...", "reason":"migrated Section 4 to _living_project.md"}
```

`/devlead status` renders it as a text chart:

```
Resume burndown:
  Apr 12:  847 █████████████████████████████
  Apr 13:  812 ████████████████████████████
  Apr 14:  749 ██████████████████████████
  Apr 15:  681 ██████████████████████
  Apr 16:  622 ████████████████████
  ...
  Phase: Burndown (trend: -45 lines/day → retirement ETA 14 days)
```

HTML dashboard version ships in v1.1.

### 18.6 New KPI — K10 Resume Leanness

Added to the KPI list (was 9, now 10).

- **Measures:** how lean `_resume.md` currently is, and whether it's trending leaner or fatter.
- **Formula:** combines current line count with 7-day delta. Current size → band (Fat / Normal / Lean / Minimal, see 18.3). 7-day delta → trend arrow.
- **Role:** [T] transparency, [P] pivot trigger.
- **Threshold:** in Fat band, positive growth for 7 days → warn (triage is falling behind). In Normal+ band, sustained growth → warn (content is being captured but not triaged out).
- **No terminal state.** K10 reports forever because `_resume.md` is permanent. A steady-state project has K10 in the Lean or Minimal band with near-zero trend.

### 18.7 Slash commands

- `/devlead resume` — print the current `_resume.md` with line count, band, and trend in the header.
- `/devlead triage` — interactive triage session: walk through untriaged items, propose a destination for each, migrate on approval.
- `/devlead migrate <section> --to <file>` — explicit migration with hash check and audit entry. Hard-blocks on destination-missing.
- `/devlead migrate rollback <id>` — undo a migration from `_migration_log.jsonl` if content loss is detected.
- `/devlead status --resume` — show leanness band + trend (text in v1, chart in v1.1).

### 18.8 How `_resume.md` interacts with `CLAUDE.md`

The two files have different roles but are **both permanent**:

| | `CLAUDE.md` | `_resume.md` |
|---|---|---|
| **Owner** | User / the project | DevLead |
| **Lifetime** | Permanent, grows over project life | Permanent, shrinks-and-grows continuously |
| **Role** | Production instructions for Claude Code | Scratchpad + triage inbox for untriaged items and session handoff |
| **Read when** | Every Claude Code session (always) | Every Claude Code session (always, first) |
| **Size** | Stable, small-to-medium | Varies; goal is always as lean as possible |

As items in `_resume.md` find proper homes, stable patterns (standing instructions, project-specific rules, design principles) can migrate INTO `CLAUDE.md` — which grows. Other content migrates into `_living_*.md` / `_project_*.md` / `_design_*.md` files. The net effect is that `_resume.md` stays lean because things flow outward from it.

The steady state: rich `CLAUDE.md` + populated `devlead_docs/` dedicated files + a **minimal but non-empty `_resume.md`** (just session handoff + 1–3 items in triage). That's the goal, and `_resume.md` never goes away.

### 18.9 Placement in v1 build plan

- **Day 3 (next session):** Add `_resume.md.tmpl` scaffold template for `/devlead init`. Add `/devlead resume` read command. Wire CLAUDE.md instruction to read `_resume.md` at session start.
- **Day 11 (Week 2):** Add `/devlead migrate` + `/devlead triage` commands with hash verification, `_migration_log.jsonl` audit, rollback.
- **Day 12 (Week 2):** Add leanness tracking (`_resume_leanness.jsonl`), wire K10, surface in `/devlead status`.
- **Day 13 (Week 2):** Wire Stop hook so Claude writes untriaged items to `_resume.md` before exit. This is the "don't lose context" guarantee.

**Timeline impact:** +1 day to the 27-day plan. New first revenue target: **2026-05-09** (was May 8). $1000 target: **2026-06-09**.

### 18.10 This file IS the first instance

The file you are reading right now (`devlead_docs/_resume.md`) IS the first `_resume.md` in existence. It was created manually in Session 2 because the triage and leanness machinery doesn't exist yet. When the migration/triage commands ship on Day 11, we will start triaging sections out (Section 1 → `_living_purpose.md`, Section 4 → `_design_section2.md`, etc.) and this file will shrink. Leanness tracking begins Day 12. The file will never retire — it will settle into a lean steady state where it holds session handoff + a small triage queue.

**Dogfood note:** DevLead's own development of this feature is tracked via this very file. If this file doesn't shrink over the build plan, the feature is broken and we should be worried.

---

## 19. Project Maturity Score (PMS) — composite metric

> **Captured 2026-04-12 (Session 2).** Nitin dictated: *"introduce a concept to give a score to project on its maturity level."* This is the spec.

### 19.1 Purpose

A single number **0–100** that answers *"how mature is this project, right now?"* Looking at the score, a user (or Claude) instantly knows whether the project is embryonic, bootstrapping, actively building, or steady-state. The number drives multiple downstream behaviors (LLM reading priority, retirement eligibility, KPI reporting discipline).

**PMS is a composite derived metric, not a KPI.** KPIs (K1–K10) are atomic measures with a single formula each. PMS is a weighted rollup over several signals — some of which ARE KPIs, some of which are state flags. Presented separately from the KPI list so it's unambiguous.

### 19.2 Formula

```
PMS = Σ (sub_score_i × weight_i) / 100
```

where each sub-score is 0–100 and weights sum to 100:

| ID | Sub-score | Weight | Source |
|---|---|---|---|
| M1 | **Interview completion** | 20 | 20 points per locked interview block (A–E). 0 to 100 linearly. |
| M2 | **Hierarchy populated** | 15 | % of BOs with weights, averaged with % of TBOs with weights, averaged with % of TBOs having ≥1 TTO. |
| M3 | **Convergence progress** | 15 | Vision-level convergence (weighted rollup from K1). 0 to 100 directly. |
| M4 | **Resume leanness** | 15 | Inverse of `_resume.md` line count. 100 if < 50 lines (Minimal); 80 if < 200 (Lean); 40 if 200–1000 (Normal); 0 if > 1000 (Fat). |
| M5 | **Living docs populated** | 10 | Fraction of `_living_*.md` files with non-placeholder content (≥ 5 lines of real text). |
| M6 | **CLAUDE.md richness** | 10 | Lines of project-specific content in `CLAUDE.md` (excluding boilerplate). 0 if stub; 100 if ≥ 50 lines. |
| M7 | **Word-keeping discipline** | 5 | K9 (Word-Keeping Ratio × 100). Only counts after ≥ 5 commitments made. Otherwise carried as N/A. |
| M8 | **Goal yield** | 5 | K8 (Goal Yield × 100). Only counts after ≥ 1 goal resolved. Otherwise N/A. |
| M9 | **Audit log depth** | 3 | `min(audit_entries / 50, 1) × 100`. Rewards projects that have been running. |
| M10 | **Pivot experience** | 2 | 100 if ≥ 1 completed pivot in `_migration_log.jsonl` or `_pivot_log.jsonl`; else 0. Pivots are evidence of iteration. |

Weights: 20+15+15+15+10+10+5+5+3+2 = **100.**

**N/A handling:** sub-scores marked N/A (M7, M8 early on) are re-weighted proportionally across the remaining scores so PMS never gets artificially suppressed.

### 19.3 Maturity bands

| PMS range | Band | What it means |
|---|---|---|
| **0–20** | **Embryonic** | Fresh install. Interview not done. `_resume.md` is the primary source of truth. |
| **21–40** | **Bootstrap** | Interview partially done. Hierarchy thin. `_resume.md` still dominant. |
| **41–60** | **Active** | Interview complete, hierarchy populated, work underway. `_resume.md` actively burning down. Dedicated files filling up. |
| **61–80** | **Mature** | Dedicated files dominant. `_resume.md` residual. Real convergence happening. K8/K9 meaningful. |
| **81–100** | **Steady State** | `CLAUDE.md` rich. Dedicated files authoritative. `_resume.md` approaching retirement. Project is self-carrying. |

**Steady state:** `PMS ≥ 85` with M4 in Lean or Minimal band is what a mature project looks like. There is no retirement gate — `_resume.md` always exists, just stays lean. The goal of driving PMS up is not to eliminate any file; it's to move the project into the Steady State band.

### 19.4 Where PMS appears

- **`/devlead status` header:** big number with band label —
  ```
  DevLead — MyProject
  Maturity: 47/100 (Active)
  Phase: Burndown   Trend: -45 lines/day   Retirement ETA: 14 days
  [... rest of status output ...]
  ```
- **`/devlead maturity`:** dedicated command that prints PMS with full sub-score breakdown —
  ```
  Project Maturity Score: 47 / 100   Band: Active

    M1  Interview completion     80/100   (weight 20)   → contributes 16.0
    M2  Hierarchy populated      60/100   (weight 15)   → contributes 9.0
    M3  Convergence progress     25/100   (weight 15)   → contributes 3.8
    M4  Resume burndown          40/100   (weight 15)   → contributes 6.0
    M5  Living docs populated    50/100   (weight 10)   → contributes 5.0
    M6  CLAUDE.md richness       30/100   (weight 10)   → contributes 3.0
    M7  Word-keeping              N/A     (< 5 commits, excluded)
    M8  Goal yield                N/A     (no goals resolved, excluded)
    M9  Audit depth             100/100   (weight 3)    → contributes 3.0
    M10 Pivot experience         50/100   (weight 2)    → contributes 1.0
                                                         ────────────
                                                         Total: 46.8 ≈ 47
  ```
- **HTML dashboard (v1.1):** progress ring with band color + sub-score breakdown.

### 19.5 How PMS drives LLM behavior

The LLM's reading priority at session start is a function of PMS — but **`_resume.md` is always read first**, regardless. The question is what comes after:

- **PMS < 40 (Embryonic/Bootstrap):** `_resume.md` first (it's fat and authoritative), then scan dedicated files for what exists.
- **PMS 40–70 (Active/early Mature):** `_resume.md` first (it's thinning out), then dedicated files for the meat of the project.
- **PMS > 70 (Mature/Steady State):** `_resume.md` first (it's lean — just handoff + triage queue), then `CLAUDE.md`, then dedicated files.

The first-read rule is invariant: Claude always reads `_resume.md` at session start, because that's where untriaged items and the session handoff live. What changes with PMS is how much OTHER content Claude needs to read to understand the project — less as the project matures.

This is how "project maturity decides the handoff" (Nitin's phrase) becomes concrete without ever taking `_resume.md` out of the loop.

### 19.6 Trend tracking

PMS is recomputed at every session start and at every `/devlead status` call. Each value is appended to `devlead_docs/_maturity_log.jsonl`:

```jsonl
{"timestamp":"2026-04-12T...", "pms":47, "band":"Active", "m1":80, "m2":60, "m3":25, "m4":40, "m5":50, "m6":30, "m9":100, "m10":50, "reason":"session_start"}
```

Slope of PMS over time tells you whether the project is actually maturing:

- **Rising:** healthy. Work is moving the project forward.
- **Flat:** warn. The project is running but not maturing. Either migrate more, or it's stuck.
- **Falling:** alarm. Extremely rare — usually means content was moved from dedicated files back into `_resume.md`, or standing instructions were retired, or a pivot undid prior work.

### 19.7 Placement in v1 build plan

- **Day 12 (Week 2):** Implement PMS formula, `/devlead maturity` command, wire into `/devlead status` header. Share audit log infrastructure from Day 11.
- **Day 17 (Week 3):** PMS gates `/devlead resume retire`.

**Timeline impact:** +0.5 day, absorbed into Week 2 buffer. First revenue target holds at **2026-05-09**.

### 19.8 Current PMS of DevLead itself (as of 2026-04-12, end Session 2)

Computed manually for dogfood:
- M1 Interview completion: 0/100 (interview hasn't been run on DevLead yet)
- M2 Hierarchy populated: 0/100 (no BOs yet)
- M3 Convergence progress: 0/100 (nothing to roll up)
- M4 Resume burndown: 0/100 (this file is huge)
- M5 Living docs populated: 0/100 (all scaffold stubs)
- M6 CLAUDE.md richness: ~40/100 (rewritten for v2, has real content)
- M7 Word-keeping: N/A
- M8 Goal yield: N/A
- M9 Audit depth: 0/100 (no audit log yet)
- M10 Pivot experience: 0/100

**Current PMS ≈ 4/100 (Embryonic).** Totally expected — we just archived v1 and wrote Section 1 of v2's design. The whole point of the next 28 days is to drive this number up.

---

## 20. Session handoff pointer (2026-04-14)

> **File split, dictated this session:** `_scratchpad.md` now holds raw untriaged capture; `_resume.md` (this file) holds session-to-session memory — locked decisions, open threads, where-we-are. Section 18 of this file currently conflates the two and needs revision — tracked in Section 13.
>
> **Where to look for the current raw capture:** `devlead_docs/_scratchpad.md` — entry dated 2026-04-14 contains the Plugin Bridge + Intake Flow directive in full.
>
> **Where the load-bearing pieces already live in THIS file:**
> - Locked principles (SSoT, zero-disruption, plugin bridge, no dark code) → Section 3.
> - Open mechanism questions (intake file set, schema, promotion, handoff) → Section 13.
> - Day-3 pivot note (interview becomes the first consumer of the bridge) → Section 14.
>
> **Next action on resume:** enter plan mode and draft the end-to-end Plugin Bridge + Intake Flow design. Plan gets approved → migrates to `_design_section2_plugin_bridge.md` → scratchpad entry shrinks to a pointer.

---

*End of resume file. Filename: `devlead_docs/_resume.md`. This file is the first read point for every new session; `_scratchpad.md` is the second. Section 18 still describes an older design where `_resume.md` was the scratchpad — that section is stale and tracked for revision in Section 13.*
