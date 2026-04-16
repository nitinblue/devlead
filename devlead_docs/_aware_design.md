# _aware_design.md

> **Self-awareness file.** Auto-generated snapshot of the project's
> current technical design. DO NOT EDIT - run `/devlead awareness` to
> refresh. Hand-edits are overwritten on next refresh.
>
> **Last refresh:** 2026-04-16T03:03:15Z
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
- **Purpose:** Bootstrap — generate the CLAUDE.md section that teaches the LLM how DevLead works.
- **Lines:** 165
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
- **Lines:** 562
- **Public API:** `main`
- **Depends on:** `devlead.install`

### `devlead.config`
- **Path:** `src/devlead/config.py`
- **Purpose:** DevLead config loader. Implements FEATURES-0009.
- **Lines:** 130
- **Public API:** `Config, load`
- **Depends on:** (stdlib only)

### `devlead.gate`
- **Path:** `src/devlead/gate.py`
- **Purpose:** DevLead Level-2 enforcement gate. Implements FEATURES-0004.
- **Lines:** 116
- **Public API:** `check_pretooluse, check_session_start, check`
- **Depends on:** `devlead.bootstrap`

### `devlead.hierarchy`
- **Path:** `src/devlead/hierarchy.py`
- **Purpose:** Parse _project_hierarchy.md into a BO/TBO/TTO tree and compute convergence.
- **Lines:** 158
- **Public API:** `TTO, TBO, BO, Sprint, parse, summary`
- **Depends on:** (stdlib only)

### `devlead.install`
- **Path:** `src/devlead/install.py`
- **Purpose:** Install command - creates devlead_docs/ in a target project and copies scaffold templates.
- **Lines:** 263
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

### `devlead.migrate`
- **Path:** `src/devlead/migrate.py`
- **Purpose:** DevLead content migration. Implements FEATURES-0006.
- **Lines:** 266
- **Public API:** `MigrationRecord, migrate, rollback, list_migrations`
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
- **Lines:** 214
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

### `devlead.verify`
- **Path:** `src/devlead/verify.py`
- **Purpose:** Cross-reference verifier for devlead_docs/. Implements FEATURES-0008.
- **Lines:** 170
- **Public API:** `VerifyReport, verify_links`
- **Depends on:** (stdlib only)

