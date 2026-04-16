# Business Convergence Engine — Design Spec

> **"I won't fly in the dark."**
> Date: 2026-04-07
> Status: DRAFT
> Author: Nitin Jain + Claude

---

## 1. Problem

DevLead governs the technical lifecycle — states, gates, hooks. But it has a blind spot: **it doesn't know if the work matters.**

Today the model asks "what do you want to work on?" — reactive, tech-first. It tracks tasks done, not business outcomes achieved. A developer can complete 50 tasks and ship nothing. The model can't tell the difference between progress and motion.

The gap:
- **No product brain.** Claude is the tech brain. Nobody forces product thinking.
- **TBOs are manually created.** The user has to know what outcomes they need. Most developers don't — they're strong builders, not product strategists.
- **No definition of done.** There's no way to say "Phase 1 is complete" in business terms. Only in task terms.
- **No weighted convergence.** A TBO worth 10% of an objective and a TBO worth 50% are treated equally.
- **No scope discipline.** New work gets added without acknowledging it's a scope change.

**Result:** The model operates without business context. It proposes work because the code needs it, not because the product needs it. Developers stay busy but don't converge on a launchable product.

## 2. Solution

A **Business Convergence Engine** that makes DevLead product-aware. The model takes ownership of the business-to-technical mapping and refuses to operate without it.

Core principle: **The model doesn't get to recommend work until it can trace that work to a business outcome. If it can't, it says "I won't fly in the dark" and explains what's missing.**

## 3. Data Model

### 3.1 Hierarchy

```
Vision (English, static, product-level north star)
  └── Business Objective (phase-scoped, frozen when accepted)
        ├── weight: points out of 100 of the phase
        ├── status: DRAFT / FROZEN / DONE
        └── TBO — Tangible Business Outcome (model-owned after BO freeze)
              ├── weight: points out of 100 of its BO
              ├── DoD: English acceptance criteria
              ├── status: NOT_STARTED / IN_PROGRESS / DONE
              └── Story (technical enabler)
                    ├── weight: points out of 100 of its TBO
                    ├── DoD: concrete acceptance criteria
                    └── Task (implementation step, fractal boundary)
```

### 3.2 Key Rules

1. **Vision** — few lines of English. North star. Never "done." Doesn't need mapping or linkage. Lives at product level, doesn't fluctuate.

2. **Business Objectives** — scoped to a phase. Written in business language ("developer can govern a project end-to-end"). The model must understand and own BOs before proposing any work. If BOs come from the user, great. Otherwise the model interviews the user and synthesizes them.

3. **TBOs** — model-owned once the BO is frozen. The model decomposes a BO into TBOs, assigns weights (must sum to 100 per BO), and writes a DoD for each. Adding a TBO after freeze = scope change. Model must flag: "This is a scope change. Accept for this phase, or defer to next phase?"

4. **Stories** — technical enablers. Weights must sum to 100 per TBO. A story may contain functional and non-functional tasks (tests, refactoring, infra). Non-functional work within a traced story is NOT shadow work — it's enabling work at the fractal boundary.

5. **Tasks** — implementation atoms. Not individually weighted. The story is the smallest unit that moves convergence. Tasks are the fractal interior — lots of work may happen inside without moving the needle, and that's fine as long as the story completes.

6. **Simple projects** — can skip TBOs. Go directly from BO to Stories. In this case, the BO acts as its own single TBO — stories hang directly off the BO with weights summing to 100. The convergence formula collapses one level: `BO_convergence = SUM(Story_weight * Story_done) / 100`.

### 3.3 BO Freeze Lifecycle

- **DRAFT** — BO is being shaped. Model or user can edit freely.
- **FROZEN** — BO is accepted. Model owns TBO decomposition. Scope is locked.
- **DONE** — All TBOs under this BO are DONE. Automatically computed, not manually set.

Who freezes: The **user** freezes a BO (it's a business decision). The model proposes BOs in DRAFT, the user reviews and freezes.

Unfreezing: A frozen BO can return to DRAFT if the decomposition is fundamentally wrong. All TBO weights become advisory until re-frozen. In-progress work continues but convergence reporting adds a caveat: "BO-2 is unfrozen — convergence is estimated."

### 3.4 Shadow Work Definition

Shadow work is ONLY work that traces to NO Business Objective. Specifically:
- A task that belongs to no story
- A story that belongs to no TBO (or no BO in simple projects)
- A TBO that belongs to no BO

Non-functional work (tests, refactoring, infra) inside a traced story is NOT shadow work. It's enabling work within the fractal.

## 4. Model Ownership Behavior

### 4.1 Three Confidence Levels

**"I own this"** — Model has vision + frozen BOs + TBO decomposition.
- Recommends next work with full traceability
- Reports convergence as a real number
- Flags scope changes when new TBOs surface
- Fully accountable to the definition of done it committed to

**"I can see the runway"** — Model has BOs but hasn't decomposed TBOs yet.
- Can do technical work the user asks for, tagging it to BOs
- Proactively compiles TBO decomposition and presents it for review
- Reports partial convergence with caveats

**"I won't fly in the dark"** — Model doesn't have enough BOs to understand what done looks like.
- Refuses to recommend development priorities
- Interviews the user to surface BOs (or synthesizes from what it knows)
- Can still do ad-hoc technical work the user insists on, but flags it as untraced
- Makes a case for WHY it can't proceed — not asking permission, stating a professional position

### 4.2 The Model as Product Brain

The model doesn't ask the user to define everything. It takes ownership:
- Reads the codebase, docs, git history, README
- Synthesizes: "Here's what I think you're building. Here are the BOs I see. Here's my TBO decomposition."
- User's job shifts from "define the work" to "review the model's understanding"
- BO compilation, TBO decomposition, story writing — all model-owned, user-reviewed
- Stories follow a consistent, structured format for easy review

### 4.3 Scope Discipline

Once a BO is frozen and TBOs are defined:
- The TBO list IS the scope
- Any new TBO = scope change, requires explicit decision
- Options: accept for this phase OR defer to next phase
- Scope drift is tracked as a metric

## 5. Bootstrap on Existing Projects

Most DevLead installs will be on existing, possibly large, codebases.

### 5.1 Bootstrap Flow

1. `devlead migrate` — sets up governance file structure (already exists)
2. Model reads everything — code, README, docs, commit history, issues
3. Model synthesizes a first draft:
   - "Here's the vision I see for this product"
   - "Here are the Business Objectives I'd define for where you are now"
   - "Here's my TBO decomposition of existing work"
   - "Here's work I found that I can't trace to any BO — potential shadow work or a BO I'm missing"
4. User reviews — corrects, adds business context the code can't reveal
5. Model freezes BOs after user approval — now owns the decomposition

### 5.2 Large Project Strategy

For large codebases, the model says: "I see 5 major subsystems. Let me bootstrap one at a time — which area is your current focus?" That becomes Phase 1.

### 5.3 Untraced Work as Signal

The most valuable bootstrap output is untraced work:
- Code that exists but maps to no BO is either:
  - A BO the model missed (user corrects — model learns)
  - Genuine shadow work (user now has visibility)

## 6. Convergence Engine

### 6.1 Weighted Convergence Formula

```
Phase_Convergence = SUM(BO_weight * BO_convergence) / 100

Where:
  BO_convergence  = SUM(TBO_weight * TBO_convergence) / 100
  TBO_convergence = SUM(Story_weight * Story_done) / 100
  Story_done      = 1 if DONE, 0 otherwise (binary at fractal boundary)
```

Weights at each level must sum to 100.

**Design decision: binary story completion.** `Story_done` is 0 or 1 — no partial credit. A story that is 90% complete contributes zero convergence until it flips to DONE. This is intentional: convergence measures delivered outcomes, not effort spent. It means convergence can stay flat during heavy development and then jump when stories land. For velocity/burndown estimates, the model may use task completion within stories as a leading indicator, but this is advisory — not part of the official convergence number.

### 6.2 Example

```
BO: "Developer can govern a project E2E" (weight: 50/100 of phase)
  TBO-1: "Install and init works"          -> 30/100 of BO
    S-001: "Package builds"                 -> 40/100 of TBO  [DONE]
    S-010: "devlead init scaffolds"         -> 60/100 of TBO  [DONE]
    TBO-1 convergence = (40*1 + 60*1)/100 = 100%

  TBO-2: "Full state lifecycle with hooks"  -> 40/100 of BO
    S-003: "State machine"                  -> 50/100 of TBO  [DONE]
    S-002: "Hook enforcement"               -> 50/100 of TBO  [NOT DONE]
    TBO-2 convergence = (50*1 + 50*0)/100 = 50%

  TBO-3: "Dashboard shows health"           -> 20/100 of BO
    TBO-3 convergence = 0%

  TBO-4: "Rollover works"                   -> 10/100 of BO
    TBO-4 convergence = 100%

  BO convergence = (30*100 + 40*50 + 20*0 + 10*100)/100 = 60%

Phase convergence (this BO's contribution) = 50 * 60% = 30 points
```

### 6.3 Coverage and Traceability

Convergence alone isn't enough. Also tracked:

- **Coverage score** — % of BO weight that has TBOs defined. If model assigned TBOs totaling only 70 out of 100, there's a 30-point gap to explain.
- **Traceability score** — % of active tasks that trace to a BO. Untraced = flagged.
- **Scope drift** — TBOs added after freeze. Tracked, not blocked.

## 7. KPI Framework — Six Instruments

All derived from the BO -> TBO -> Story -> Task hierarchy plus effort data (tokens, time) that DevLead already captures.

### 7.1 Convergence — "Are we getting there?"

| Metric | Formula | Signal |
|--------|---------|--------|
| Phase convergence | Weighted sum (Section 6.1) | 0-100, the master number |
| Per-BO convergence | Same formula, scoped to one BO | Which objectives are lagging |
| Velocity | Convergence delta per session | Are we accelerating or stalling |
| Burndown | Convergence needed / velocity | When does this phase hit 100% |

### 7.2 Going in Circles — "Are we stuck?"

| Metric | Formula | Signal |
|--------|---------|--------|
| Rework ratio | `rework_tokens / total_tokens` (last N sessions) | High = spinning wheels |
| Zero-delta sessions | Count of sessions where convergence didn't move | 3 in a row = alarm |
| Story regression | Stories that went DONE -> reopened | Decomposition was wrong |
| Task churn | Tasks created and abandoned within same session | Model is guessing |

### 7.3 Skin in the Game — "Is work traced to outcomes?"

| Metric | Formula | Signal |
|--------|---------|--------|
| Traceability | `traced_tasks / total_tasks` | % of work that maps to a BO |
| Coverage | `assigned_TBO_weight / 100` per BO | Holes in decomposition |
| Model confidence | Composite of traceability + coverage | Below threshold = "won't fly in the dark" |

### 7.4 Time Investment — "Where does time go?"

| Metric | Formula | Signal |
|--------|---------|--------|
| Effort per BO/TBO/Story | Session duration allocated to each | Where the clock goes |
| Effort vs weight ratio | `effort_share - weight_share` per TBO | Positive = over-invested, negative = under-invested |
| Burndown estimate | Remaining convergence / velocity | Projected completion |

### 7.5 Tokenomics — "What's the AI cost per outcome?"

| Metric | Formula | Signal |
|--------|---------|--------|
| Tokens per convergence point | `total_tokens / convergence_delta` | Efficiency of AI spend |
| Tokens per BO/TBO | Token allocation by business outcome | Where is the AI budget going |
| Cost trend | Tokens-per-point over time | Improving (learning) or degrading (complexity/circles) |

### 7.6 Shadow Work — "What's wasted?"

| Metric | Formula | Signal |
|--------|---------|--------|
| Shadow ratio | `untraced_effort / total_effort` | % of work with no business trace |
| Shadow token ratio | `shadow_tokens / total_tokens` | AI budget spent on nothing |
| Shadow trend | Shadow ratio over time | Growing = model is drifting |
| Shadow breakdown | Categories: gold-plating, yak-shaving, unplanned detours | What kind of waste |

### 7.7 Alarm Conditions

Each KPI has a healthy range and an alarm. When alarms fire, the model surfaces them before proposing work:

| KPI | Alarm Condition |
|-----|-----------------|
| Convergence | Velocity = 0 for 3+ sessions |
| Going in Circles | Rework ratio > 40% |
| Skin in the Game | Traceability < 70% triggers "won't fly in the dark" |
| Time Investment | Effort/weight divergence > 3x on any TBO |
| Tokenomics | Cost-per-point increasing 3 sessions in a row |
| Shadow Work | Shadow ratio > 20% |

Thresholds are configurable in `devlead.toml`. These are defaults.

## 8. Session Start Behavior

At session start, the model reads the instrument panel and reports:

> "Phase 1: 62% converged. BO-1 at 85% (TBO-2 remaining). BO-2 hasn't moved.
> 2 tasks from last session untraced. Shadow ratio: 8%.
> Tokenomics: 1,200 tokens/point (improving).
> I own this. Recommended: finish TBO-2 (40% BO weight, 50% complete — highest leverage)."

Or:

> "I won't fly in the dark. I have 3 BOs but haven't decomposed TBOs for BO-2 and BO-3.
> I can't recommend priorities because I don't know what done looks like for 60% of this phase.
> I need 10 minutes of your product thinking to decompose these objectives."

## 9. Files and Storage

| File | Content |
|------|---------|
| `devlead_docs/_living_vision.md` | Vision statement (static, few lines) |
| `devlead_docs/_living_business_objectives.md` | BOs with phase, weights, TBO decomposition |
| `devlead_docs/_project_stories.md` | Stories with TBO linkage, weights, DoD |
| `devlead_docs/_project_tasks.md` | Tasks with story linkage (existing) |
| `devlead.toml` | KPI thresholds, alarm configs (existing) |
| `devlead_docs/session_history.jsonl` | Per-session convergence snapshots (existing) |

### 9.1 Vision File Format

```markdown
# Product Vision

> Type: LIVING

DevLead is project governance for AI-assisted development. It ensures that every
AI session is disciplined, plan-driven, and aligned with business objectives.
Lead your development. Don't let AI wander.
```

### 9.2 BO File Format

```markdown
## Phase 1: MVP

| ID | Objective | Weight | Status |
|----|-----------|--------|--------|
| BO-1 | Developer can govern a project E2E without manual setup | 50 | FROZEN |
| BO-2 | Multi-project portfolio governance works | 30 | FROZEN |
| BO-3 | Available on PyPI as installable package | 20 | FROZEN |

### BO-1: Developer can govern a project E2E without manual setup

| TBO | Description | Weight | DoD | Status |
|-----|-------------|--------|-----|--------|
| TBO-1 | Install and run devlead init | 30 | pip install + init creates full scaffold | DONE |
| TBO-2 | Full state lifecycle with hooks | 40 | 7-state lifecycle enforced via hooks | IN_PROGRESS |
| TBO-3 | Dashboard shows project health | 20 | HTML dashboard with KPIs and trends | DONE |
| TBO-4 | Rollover archives cleanly | 10 | Monthly rollover preserves open items | DONE |
```

## 10. Future: RL Pipeline

Phase 2 opportunity. As DevLead governs more projects and accumulates data:
- What weights were assigned vs what actually drove completion
- Where scope changes happened
- Which decompositions were accurate vs needed revision
- Token efficiency curves across project types

This data becomes a training signal for a reinforcement learning model that improves weight assignment, decomposition quality, and alarm thresholds. The infrastructure (session_history.jsonl, effort tracking, token counts) is already being built.

Not in scope for this phase. Documented as a future TBO.

## 11. What Changes from Current Design

| Current | New |
|---------|-----|
| TBOs are manually created by user | Model owns TBO decomposition after BO freeze |
| No Business Objectives as first-class concept | BOs are the top-level deliverable with weights |
| No vision file | `_living_vision.md` added |
| Convergence = count-based (TBOs done / total) | Convergence = weighted sum, rolling up from stories |
| No scope discipline | TBO additions after freeze = explicit scope change |
| Model asks "what to work on?" | Model says "here's what matters and why" or "I won't fly in the dark" |
| KPIs are technical metrics | 6 KPIs tied to business convergence |
| Shadow work = task with no story | Shadow work = anything that doesn't trace to a BO |
| Bootstrap = file structure only | Bootstrap = model synthesizes BOs from existing codebase |

## 12. Architecture Boundary: DevLead vs Claude Code

DevLead is a **CLI tool**. It provides data structures, file formats, convergence formulas, and enforcement via hooks. It does NOT contain an LLM.

The "model as product brain" behavior (Sections 4.1-4.2) is **Claude Code's behavior**, guided by CLAUDE.md instructions that DevLead scaffolds. The split:

| Responsibility | Owner |
|---------------|-------|
| BO/TBO/Story file format and parsing | DevLead CLI |
| Convergence formula computation | DevLead CLI (`devlead status`, `devlead kpis`) |
| Weight validation (sums to 100) | DevLead CLI |
| Scope change detection | DevLead CLI (hook) |
| "I won't fly in the dark" decision | Claude Code (via CLAUDE.md instructions) |
| BO/TBO synthesis from codebase | Claude Code (LLM reasoning) |
| User interview for BOs | Claude Code (conversation) |
| Writing BOs/TBOs to devlead_docs | Claude Code (writes files DevLead validates) |

DevLead provides the instruments. Claude Code flies the plane.

## 13. Migration from Current Data Model

### 13.1 What Changes

Current: flat TBO list in `_living_business_objectives.md`, no BOs, no weights, count-based convergence.
Target: BO → TBO → Story hierarchy with weights at every level.

### 13.2 Migration Strategy

`devlead migrate` (already exists) will be extended:

1. Wrap all existing TBOs under a single default BO ("Phase 1") with weight 100
2. Assign equal weights to existing TBOs (100 / N per TBO)
3. Assign equal weights to stories within each TBO (100 / M per story)
4. Mark default BO as DRAFT (user must review and freeze)
5. Create `_living_vision.md` with placeholder text

Model-assigned weights are DRAFT until user confirms. The `weight_source` is tracked: `MODEL_ASSIGNED` vs `USER_CONFIRMED`.

### 13.3 Existing KPIs

The 6 new KPI instruments supplement the existing 30 KPIs in `kpi_engine.py`. The existing KPIs are technical metrics (delivery, project health, LLM effectiveness). The new 6 are business convergence metrics. They coexist — the dashboard gets a new "Convergence" section alongside existing KPI tabs.

### 13.4 KPI Data Collection Gaps

Some new KPIs require data not yet collected:

| KPI Metric | Gap | Solution |
|-----------|-----|----------|
| Rework tokens | No rework classification | Tag tokens as rework when a story regresses (DONE → reopened) |
| Story regression | No status history | Add status log to session_history.jsonl |
| Task churn | No creation-session tracking | Add `created_session` field to task entries |
| Shadow breakdown categories | No classification mechanism | Model-assigned via CLAUDE.md instructions, stored as task metadata |

These are implementation tasks, not spec gaps. Each becomes a story.

## 14. Gate Enforcement Philosophy

DevLead's gates enforce **information flow**, not file writes:
- **devlead_docs/** — system of record, enforced (log level)
- **memory/** — derived from devlead_docs only, enforced (log level)
- **Everything else** — logged, never blocked

The state machine governs the development lifecycle. Gates ensure docs stay authoritative. But the model should never be blocked from writing code, specs, or working artifacts. Log it, don't block it. No blockers.
