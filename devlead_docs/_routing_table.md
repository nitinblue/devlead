# DevLead Routing Table

<!-- devlead:sot
  purpose: "Intent-to-responsibility routing for all DevLead actions"
  owner: "user"
  canonical_for: ["responsibility_routing"]
  lineage:
    receives_from: ["user dictation"]
    migrates_to: []
  lifetime: "permanent"
  last_audit: "2026-04-16"
-->

## How to use this file

**Read this file at the start of every session, before responding to any user input.**

When the user says something, classify their intent against the responsibilities below. If a match is found, follow the steps exactly — no improvisation, no skipping. If no match is found, proceed as business-as-usual (LLM unguided).

**To add a new responsibility:** append a new `## R<N>` section following the same format. No code changes needed.

---

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
