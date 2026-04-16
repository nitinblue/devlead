# _aware_design.md

<!-- devlead:sot
  purpose: "Auto-derived inventory of Python modules"
  owner: "system"
  canonical_for: ["module_inventory"]
  lineage:
    receives_from: ["src/ scan"]
    migrates_to: []
  lifetime: "regenerated"
  last_audit: "2026-04-15"
-->


> **Self-awareness file.** Auto-generated snapshot of the project's
> current technical design. DO NOT EDIT - run `/devlead awareness` to
> refresh. Hand-edits are overwritten on next refresh.
>
> **Last refresh:** 2026-04-15T02:05:43Z
> **Generator:** devlead.awareness v1
> **Scan source:** src/devlead/*.py (module docstrings + public API + deps)

---

## Modules

### `devlead.awareness`
- **Path:** `src/devlead/awareness.py`
- **Purpose:** Self-awareness layer - generates _aware_*.md files from the codebase.
- **Lines:** 240
- **Public API:** `Feature, Module, ProjectSnapshot, scan, render_features, render_design, refresh`
- **Depends on:** (stdlib only)

### `devlead.bridge`
- **Path:** `src/devlead/bridge.py`
- **Purpose:** Plugin bridge - ingest a plugin plan OR a scratchpad entry into an intake file.
- **Lines:** 240
- **Public API:** `ingest, ingest_from_scratchpad`
- **Depends on:** (stdlib only)

### `devlead.cli`
- **Path:** `src/devlead/cli.py`
- **Purpose:** Command-line dispatch for DevLead.
- **Lines:** 212
- **Public API:** `main`
- **Depends on:** `devlead.install`

### `devlead.install`
- **Path:** `src/devlead/install.py`
- **Purpose:** Install command - creates devlead_docs/ in a target project and copies scaffold templates.
- **Lines:** 148
- **Public API:** `InstallReport, install`
- **Depends on:** (stdlib only)

### `devlead.intake`
- **Path:** `src/devlead/intake.py`
- **Purpose:** Intake file layer - read/write any `_intake_*.md` file.
- **Lines:** 232
- **Public API:** `IntakeEntry, prefix_from_path, template_path_for, read, next_id, add_entry`
- **Depends on:** (stdlib only)

### `devlead.scratchpad`
- **Path:** `src/devlead/scratchpad.py`
- **Purpose:** Scratchpad helpers - read/append/iterate/convert entries in _scratchpad.md.
- **Lines:** 181
- **Public API:** `read, append_entry, iter_untriaged, get_entry, append_cross_reference`
- **Depends on:** (stdlib only)

