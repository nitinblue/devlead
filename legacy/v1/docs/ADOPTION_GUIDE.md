# Adopting DevLead on an Existing Project

A field guide based on migrating **eTrading** (Trading CoTrader) — a 60-session, 620+ test, multi-agent options trading platform — to DevLead governance.

---

## Migration is Two Phases

| Phase | Command | What happens |
|-------|---------|-------------|
| **Phase 1: Scaffold** | `devlead migrate` | Creates empty `devlead_docs/` structure, merges hooks, appends CLAUDE.md. **Done.** |
| **Phase 2: Populate** | `devlead migrate --populate` | Parses existing docs and fills `devlead_docs/` with real content. **TODO — needs building.** |

Phase 1 is init. Phase 2 is the actual migration. Without Phase 2, you have empty templates next to your real docs — two sources of truth, both incomplete.

---

## What Phase 1 Does (already implemented)

```bash
cd /path/to/your-project
devlead migrate
```

### Output

```
─── Existing Files Detected ───────────────
  • CLAUDE.md
  • .claude/settings.json
  • docs/PROJECT_TASKS.md

─── Migration Report ──────────────────────
  Created:
    ✓ devlead_docs/                          # governance directory
    ✓ devlead_docs/_project_status.md        # empty template
    ✓ devlead_docs/_project_tasks.md         # empty template
    ✓ devlead_docs/_project_roadmap.md       # empty template
    ✓ devlead_docs/_project_stories.md       # empty template
    ✓ devlead_docs/_intake_features.md       # empty template
    ✓ devlead_docs/_intake_issues.md         # empty template
    ✓ devlead_docs/_intake_bugs.md           # empty template
    ✓ devlead_docs/_intake_gaps.md           # empty template
    ✓ devlead_docs/_living_standing_instructions.md  # minimal rules
    ✓ devlead_docs/_living_business_objectives.md    # placeholder BO
    ✓ devlead_docs/_living_distribution.md   # empty template
    ✓ devlead_docs/_living_vision.md         # empty template
    ✓ devlead.toml                           # config with defaults
    ✓ .claude/settings.json (hooks merged)   # state machine hooks
    ✓ CLAUDE.md (DevLead section appended)   # governance rules
```

**Key behaviors:**
- Never overwrites existing files
- Hooks are *merged* into existing `.claude/settings.json`
- CLAUDE.md gets a governance section *appended* at the bottom
- State machine gates default to "warn" (suggest, don't block)

---

## What Phase 2 Should Do (needs building)

`devlead migrate --populate` should parse existing project docs and fill the empty templates with real content. This is the hard part.

### Content Source Map

The migrate command already detects existing files via `scan_existing()`. Phase 2 extends this: for each detected file, extract structured content into the right devlead_docs target.

#### From CLAUDE.md

| CLAUDE.md Section | Target | Extraction |
|-------------------|--------|------------|
| Prime Directive, Non-Negotiable Rules | `_living_standing_instructions.md` | Rules, coding standards, system boundaries |
| "Where We Are Now" | `_project_status.md` | Current state, priorities |
| Pipeline description, vision | `_living_vision.md` | What the system does and why |
| Coding Standards | `_living_standing_instructions.md` | Append as coding standards section |
| Dev Commands | `_living_standing_instructions.md` | Append as dev commands section |

#### From docs/ directory

| Source File | Target | Extraction |
|-------------|--------|------------|
| `PROJECT_STATE.md` | `_project_status.md` | Merge current state snapshot |
| `PROJECT_TASKS.md` | `_project_tasks.md` | Parse task table rows |
| `PROJECT_SPEC.md` | `_living_vision.md` + `_living_business_objectives.md` | Split: vision vs objectives |
| `GAPS.md` | `_intake_gaps.md` | Open gaps as intake items |
| `PRODUCT_STRATEGY.md` | `_living_business_objectives.md` | Extract BOs |
| `PHASE2_*.md` | `_project_roadmap.md` | Extract epics/phases |

#### From memory/ intake files (if present)

| Source | Target | Extraction |
|--------|--------|------------|
| `memory/bugs_intake.md` | `_intake_bugs.md` | Copy active items |
| `memory/features_intake.md` | `_intake_features.md` | Copy active items |
| `memory/gaps_intake.md` | `_intake_gaps.md` | Copy active items |
| `memory/risks_intake.md` | `_intake_issues.md` | Copy active items |

### What It Should NOT Do

- **Don't delete old files.** Mark them with a deprecation notice pointing to the devlead_docs equivalent.
- **Don't migrate architecture docs.** `CONTAINER_ARCHITECTURE.md`, `TESTING_GUIDE.md`, etc. stay in `docs/`. DevLead tracks governance, not system design.
- **Don't migrate auto-memory.** `.claude/projects/*/memory/` is per-conversation context, not governance.
- **Don't try to be perfect.** Extract what's parseable, leave the rest for the user to review.

### Deprecation Notice (injected into old files)

After extracting content, Phase 2 prepends a notice to the source file:

```markdown
> **DEPRECATED** — This file has been migrated to DevLead governance.
> Source of truth: `devlead_docs/_project_tasks.md`
> This file is kept for reference only. Do not update it.
```

---

## Plugin Integration (Superpowers)

Superpowers writes specs and plans to hardcoded paths:

| Skill | Default Path | Override Mechanism |
|-------|-------------|-------------------|
| `brainstorming` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` | User preferences in CLAUDE.md |
| `writing-plans` | `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md` | User preferences in CLAUDE.md |

### Redirect to devlead_docs

`devlead migrate` should append the following to CLAUDE.md (in the DevLead Governance section) to redirect superpowers output:

```markdown
### Plugin Output Paths

When using superpowers skills:
- Save specs to: `devlead_docs/specs/YYYY-MM-DD-<topic>-design.md`
- Save plans to: `devlead_docs/plans/YYYY-MM-DD-<feature-name>.md`

These paths override the superpowers defaults. All design artifacts live under `devlead_docs/`.
```

This works because superpowers explicitly states: *"User preferences for spec/plan location override this default."*

### Implementation in migrate.py

Add to `_DEVLEAD_CLAUDE_MD_SECTION`:

```python
### Plugin Output Paths

When using superpowers skills:
- Save specs to: `devlead_docs/specs/YYYY-MM-DD-<topic>-design.md`
- Save plans to: `devlead_docs/plans/YYYY-MM-DD-<feature-name>.md`

These paths override the superpowers defaults.
```

And in `do_migrate()`, create the subdirectories:

```python
(docs_dir / "specs").mkdir(exist_ok=True)
(docs_dir / "plans").mkdir(exist_ok=True)
```

---

## Configuration

### devlead.toml

```toml
[project]
name = "YourProject"
docs_dir = "devlead_docs"

[kpis]
circles_warning = 50        # warn if rework rate exceeds this
ftr_minimum = 60            # first-time-right minimum %
convergence_target = 80     # target convergence score

[paths]
memory_policy = "warn"      # "log" | "warn" | "block"
docs_policy = "warn"        # controls writes to devlead_docs outside UPDATE state

[scope]
enforcement = "log"         # "log" | "warn" | "block"

[audit]
enabled = true

[[gates]]
name = "memory-from-docs"
trigger = "Edit|Write"
path = "**/.claude/*/memory/**"
condition = "state_not_in(UPDATE, SESSION_END)"
action = "warn"                                    # suggest, don't block
message = "Memory must derive from devlead_docs. Transition to UPDATE first."

[[gates]]
name = "protect-docs"
trigger = "Edit|Write"
path = "**/devlead_docs/**"
condition = "state_not_in(UPDATE, SESSION_END)"
action = "warn"
message = "Editing devlead_docs outside UPDATE state."
```

**All gates default to "warn".** States are suggestions, not enforcement. Users who want strict enforcement can change individual gates to "block".

---

## The State Machine

```
ORIENT → INTAKE → PLAN → EXECUTE → UPDATE → SESSION_END
```

| State | Purpose | Exit criteria |
|-------|---------|---------------|
| **ORIENT** | Read docs, report KPIs | Read status, tasks, intake; report to user |
| **INTAKE** | Capture user requests | All requests in intake files, triaged |
| **PLAN** | Design before coding | Plan approved |
| **EXECUTE** | Write code | Scope-locked to planned files |
| **UPDATE** | Update governance docs | Status, tasks, intake updated |
| **SESSION_END** | Close out | Rollover incomplete work |

States are **suggestions by default**. The state machine tracks where you are and warns if you skip steps, but it won't block your work. This is DevLead guiding, not gatekeeping.

---

## Post-Migration Checklist

After running `devlead migrate` (Phase 1), verify:

- [ ] `devlead_docs/` exists with 12+ template files
- [ ] `devlead.toml` exists with correct project name
- [ ] `.claude/settings.json` has DevLead hooks merged
- [ ] `CLAUDE.md` has "DevLead Governance" section at bottom
- [ ] `devlead status` runs without errors

After Phase 2 (manual or `--populate`):

- [ ] `_living_business_objectives.md` has at least one real BO
- [ ] `_project_status.md` reflects current state
- [ ] `_project_tasks.md` has active backlog
- [ ] `_intake_*.md` files have active items from old intake files
- [ ] Old docs have deprecation notices
- [ ] `devlead status` shows convergence > 0%
- [ ] Superpowers specs/plans writing to `devlead_docs/specs/` and `devlead_docs/plans/`

---

## What to Keep vs Retire

### Keep as-is (don't migrate)
- **Architecture docs** (`CONTAINER_ARCHITECTURE.md`, `TESTING_GUIDE.md`) — system design, not governance
- **Feature docs** (`KNACK_CURRICULUM.md`, etc.) — domain knowledge
- **Auto-memory** (`.claude/projects/*/memory/`) — per-conversation, not governance
- **Code, tests, git history** — obviously

### Migrate then deprecate
- `GAPS.md` → `_intake_gaps.md`
- `docs/PROJECT_TASKS.md` → `_project_tasks.md`
- `docs/PROJECT_STATE.md` → `_project_status.md`
- `docs/PROJECT_SPEC.md` → `_living_vision.md` + `_living_business_objectives.md`
- `memory/*_intake.md` → `devlead_docs/_intake_*.md`

### Redirect
- `docs/superpowers/specs/` → `devlead_docs/specs/`
- `docs/superpowers/plans/` → `devlead_docs/plans/`

---

## Common Pitfalls

### 1. Running Phase 1 and thinking you're done
The templates are empty. Without Phase 2, you have two doc structures — old (real content) and new (empty). This is worse than no migration.

### 2. Duplicate sources of truth
The #1 risk. If `GAPS.md` and `_intake_gaps.md` both exist with different content, confusion follows. Deprecation notices on old files are critical.

### 3. Leaving BOs empty
DevLead's convergence score will be 0% with no Business Objectives. Define at least your top-level BOs immediately after Phase 1.

### 4. Migrating architecture docs into devlead_docs
Don't. `devlead_docs/` is governance (what, why, when). Architecture docs are system design (how). Different concerns, different update cadences.

### 5. Superpowers still writing to old paths
Without the CLAUDE.md path override, specs and plans keep going to `docs/superpowers/`. Add the redirect instruction to CLAUDE.md or wait for `devlead migrate` to inject it automatically.

---

## Quick Reference

| Command | What it does |
|---------|-------------|
| `devlead migrate` | Phase 1: scaffold empty structure |
| `devlead migrate --populate` | Phase 2: extract content from existing docs (TODO) |
| `devlead migrate --dry-run` | Preview what migrate would do |
| `devlead start` | Begin a governed session |
| `devlead status` | Show convergence, KPIs, open tasks |
| `devlead gate` | Run phase gate check |
| `devlead transition` | Move to next state |
| `devlead checklist` | Show/verify phase checklist |
| `devlead rollover` | Roll incomplete work forward |
| `devlead doctor` | Diagnose project health |
| `devlead audit` | Show file write audit log |
| `devlead gap` | Detect governance gaps |
| `devlead view` | Show BO → Story → Task hierarchy |
| `devlead analyze` | Smart project analysis by TBO |
| `devlead triage` | Triage scratchpad into intake |
