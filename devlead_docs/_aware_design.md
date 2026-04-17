# _aware_design.md

> **Self-awareness file.** Auto-generated snapshot of the project's
> current technical design. DO NOT EDIT - run `/devlead awareness` to
> refresh. Hand-edits are overwritten on next refresh.
>
> **Last refresh:** 2026-04-17T05:03:44Z
> **Generator:** devlead.awareness v1
> **Scan source:** src/devlead/*.py (module docstrings + public API + deps)

---

## Modules

### `devlead.audit`
- **Path:** `src/devlead/audit.py`
- **Purpose:** DevLead audit log writer. Implements FEATURES-0010.
- **Lines:** 70
- **Public API:** `append_event, tail`
- **Depends on:** (stdlib only)

### `devlead.awareness`
- **Path:** `src/devlead/awareness.py`
- **Purpose:** Self-awareness layer - generates _aware_*.md files from the codebase.
- **Lines:** 240
- **Public API:** `Feature, Module, ProjectSnapshot, scan, render_features, render_design, refresh`
- **Depends on:** (stdlib only)

### `devlead.bootstrap`
- **Path:** `src/devlead/bootstrap.py`
- **Purpose:** Bootstrap — generate CLAUDE.md section 100% derived from devlead_docs/ files.
- **Lines:** 223
- **Public API:** `generate_section, write_claude_md, generate_session_context`
- **Depends on:** (stdlib only)

### `devlead.bridge`
- **Path:** `src/devlead/bridge.py`
- **Purpose:** Plugin bridge - ingest a plugin plan OR a scratchpad entry into an intake file.
- **Lines:** 301
- **Public API:** `ingest, ingest_from_scratchpad, promote_to_living`
- **Depends on:** (stdlib only)

### `devlead.cli`
- **Path:** `src/devlead/cli.py`
- **Purpose:** Command-line dispatch for DevLead.
- **Lines:** 735
- **Public API:** `main`
- **Depends on:** `devlead.install`

### `devlead.config`
- **Path:** `src/devlead/config.py`
- **Purpose:** DevLead config loader. Implements FEATURES-0009.
- **Lines:** 130
- **Public API:** `Config, load`
- **Depends on:** (stdlib only)

### `devlead.convergence`
- **Path:** `src/devlead/convergence.py`
- **Purpose:** Convergence math layer for DevLead.
- **Lines:** 190
- **Public API:** `dot, norm, cosine, compute_g, compute_s, compute_C, compute_alpha, compute_phi, compute_epsilon, compute_gravity, compute_gram`
- **Depends on:** (stdlib only)

### `devlead.dashboard`
- **Path:** `src/devlead/dashboard.py`
- **Purpose:** 10-tab project management dashboard. Static HTML, CSS-only tabs, no JavaScript.
- **Lines:** 550
- **Public API:** `generate, write_dashboard`
- **Depends on:** (stdlib only)

### `devlead.effort`
- **Path:** `src/devlead/effort.py`
- **Purpose:** Effort tracking — record and aggregate per-TTO engineering attribution.
- **Lines:** 135
- **Public API:** `record_effort, get_tto_effort, get_tbo_effort, get_bo_effort, get_all_effort, summary`
- **Depends on:** (stdlib only)

### `devlead.gate`
- **Path:** `src/devlead/gate.py`
- **Purpose:** DevLead Level-2 enforcement gate. Implements FEATURES-0004.
- **Lines:** 305
- **Public API:** `check_pretooluse, check_session_start, check_user_prompt, check_stop, check`
- **Depends on:** `devlead.bootstrap`

### `devlead.hierarchy`
- **Path:** `src/devlead/hierarchy.py`
- **Purpose:** Parse _project_hierarchy.md into a BO/TBO/TTO tree and compute convergence.
- **Lines:** 306
- **Public API:** `TTO, TBO, BO, Sprint, parse, coverage_score, tbo_coverage_score, traceability_score, convergence_breakdown, summary`
- **Depends on:** (stdlib only)

### `devlead.install`
- **Path:** `src/devlead/install.py`
- **Purpose:** Install command - creates devlead_docs/ in a target project and copies scaffold templates.
- **Lines:** 287
- **Public API:** `InstallReport, install, install_addon`
- **Depends on:** `devlead.bootstrap`

### `devlead.intake`
- **Path:** `src/devlead/intake.py`
- **Purpose:** Intake file layer - read/write any `_intake_*.md` file.
- **Lines:** 297
- **Public API:** `IntakeEntry, prefix_from_path, template_path_for, read, next_id, add_entry, find_entry, list_by_status, update_status`
- **Depends on:** (stdlib only)

### `devlead.kpi`
- **Path:** `src/devlead/kpi.py`
- **Purpose:** KPI engine for DevLead v2. Implements TTO-006 under BO-001/TBO-003.
- **Lines:** 399
- **Public API:** `KpiResult, compute, record_session, summary`
- **Depends on:** (stdlib only)

### `devlead.metric_source`
- **Path:** `src/devlead/metric_source.py`
- **Purpose:** Metric source adapter — manual mode for v1.
- **Lines:** 123
- **Public API:** `record_reading, read_history, read_latest, latest_values, apply_to_sprints`
- **Depends on:** (stdlib only)

### `devlead.migrate`
- **Path:** `src/devlead/migrate.py`
- **Purpose:** DevLead content migration. Implements FEATURES-0006.
- **Lines:** 266
- **Public API:** `MigrationRecord, migrate, rollback, list_migrations`
- **Depends on:** (stdlib only)

### `devlead.project_init`
- **Path:** `src/devlead/project_init.py`
- **Purpose:** project-init CLI — cold-start onboarding for a new DevLead project.
- **Lines:** 292
- **Public API:** `Question, interview, write_answers, hash_hierarchy, lock_hierarchy, generate_intake_from_ttos`
- **Depends on:** `devlead.hierarchy`

### `devlead.promise_ledger`
- **Path:** `src/devlead/promise_ledger.py`
- **Purpose:** Promise ledger — captures what each TTO promised vs what reality delivered.
- **Lines:** 276
- **Public API:** `append_promise, read_all, collect_bo_metrics, write_promises_for, run_realisation_sweep`
- **Depends on:** `devlead.hierarchy`

### `devlead.render`
- **Path:** `src/devlead/render.py`
- **Purpose:** Markdown → HTML renderer for devlead_docs/ files.
- **Lines:** 325
- **Public API:** `render_md_to_html, render_md_to_full_html, render_dir`
- **Depends on:** (stdlib only)

### `devlead.report`
- **Path:** `src/devlead/report.py`
- **Purpose:** Session report — plain-English HTML that a non-coder can read to verify what Claude did.
- **Lines:** 333
- **Public API:** `generate, write_report`
- **Depends on:** (stdlib only)

### `devlead.resume`
- **Path:** `src/devlead/resume.py`
- **Purpose:** Auto-generate _resume.md from real project state. Not Claude's opinion.
- **Lines:** 405
- **Public API:** `generate, refresh`
- **Depends on:** (stdlib only)

### `devlead.scratchpad`
- **Path:** `src/devlead/scratchpad.py`
- **Purpose:** Scratchpad helpers - read/append/iterate/convert entries in _scratchpad.md.
- **Lines:** 307
- **Public API:** `read, append_entry, iter_untriaged, get_entry, append_cross_reference, archive_promoted`
- **Depends on:** (stdlib only)

### `devlead.sot`
- **Path:** `src/devlead/sot.py`
- **Purpose:** Source-of-truth (SOT) declaration blocks. Implements FEATURES-0005.
- **Lines:** 183
- **Public API:** `SotBlock, parse, parse_text, render, read_all`
- **Depends on:** (stdlib only)

### `devlead.verifier`
- **Path:** `src/devlead/verifier.py`
- **Purpose:** Verify runner — runs every TTO verify: command and updates hierarchy checkboxes.
- **Lines:** 112
- **Public API:** `VerifyResult, run_all, update_hierarchy, summary`
- **Depends on:** (stdlib only)

### `devlead.verify`
- **Path:** `src/devlead/verify.py`
- **Purpose:** Cross-reference verifier for devlead_docs/. Implements FEATURES-0008.
- **Lines:** 170
- **Public API:** `VerifyReport, verify_links`
- **Depends on:** (stdlib only)

