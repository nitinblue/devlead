# DevLead Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build DevLead — a Python CLI that governs AI-assisted development via state machine, hooks, KPIs, and a living document model.

**Architecture:** Pure Python 3.11+ package with zero external dependencies. src-layout. CLI entry point via pyproject.toml. State machine enforced via Claude Code hooks. 30 built-in KPIs + custom TOML/plugin extensibility. Multi-project portfolio support.

**Tech Stack:** Python stdlib only (json, pathlib, tomllib, datetime, re, shutil, importlib, textwrap, dataclasses)

**Spec:** `docs/2026-04-05-devlead-design.md`

---

## Task 0: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/devlead/__init__.py`
- Create: `src/devlead/cli.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `.gitignore`
- Test: `tests/test_smoke.py`

- [ ] **Step 1: Write smoke test**

```python
# tests/test_smoke.py
import subprocess
import sys

def test_import():
    import devlead
    assert hasattr(devlead, "__version__")

def test_cli_runs():
    result = subprocess.run([sys.executable, "-m", "devlead"], capture_output=True, text=True)
    assert result.returncode == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd C:/Users/nitin/plugin-development/devlead && python -m pytest tests/test_smoke.py -v`
Expected: ImportError

- [ ] **Step 3: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "devlead"
version = "0.1.0"
description = "Lead your development. Don't let AI wander."
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Nitin Jain"}]

[project.scripts]
devlead = "devlead.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: Create package files**

```python
# src/devlead/__init__.py
"""DevLead — Lead your development. Don't let AI wander."""
__version__ = "0.1.0"
```

```python
# src/devlead/__main__.py
from devlead.cli import main
main()
```

```python
# src/devlead/cli.py
"""DevLead CLI entry point."""
import sys

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print("devlead — Lead your development. Don't let AI wander.")
        print("Usage: devlead <command> [args]")
        print("Commands: init, start, status, gate, transition, checklist, kpis, rollover, doctor, portfolio, collab")
        return 0
    if sys.argv[1] == "--version":
        from devlead import __version__
        print(f"devlead {__version__}")
        return 0
    print(f"devlead: unknown command '{sys.argv[1]}'", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
```

```python
# tests/__init__.py
```

```python
# tests/conftest.py
"""Shared test fixtures for DevLead."""
import json
from pathlib import Path
import pytest

@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project directory with claude_docs/."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    return tmp_path

@pytest.fixture
def tmp_docs(tmp_project):
    """Return the claude_docs/ directory inside tmp_project."""
    return tmp_project / "claude_docs"

@pytest.fixture
def state_file(tmp_docs):
    """Return path to session_state.json."""
    return tmp_docs / "session_state.json"
```

- [ ] **Step 5: Create .gitignore**

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/
*.egg
.venv/
.pytest_cache/
claude_docs/session_state.json
```

- [ ] **Step 6: Install and verify**

```bash
cd C:/Users/nitin/plugin-development/devlead
pip install -e .
python -m pytest tests/test_smoke.py -v
devlead --help
devlead --version
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: project skeleton — pyproject.toml, src layout, CLI stub"
```

---

## Task 1: hooks.py — Hook Output Helpers

**Files:**
- Create: `src/devlead/hooks.py`
- Test: `tests/test_hooks.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_hooks.py
import json
import pytest
from devlead.hooks import hook_allow, hook_block, hook_context

def test_hook_allow_exits_zero():
    with pytest.raises(SystemExit) as exc:
        hook_allow()
    assert exc.value.code == 0

def test_hook_allow_outputs_json(capsys):
    with pytest.raises(SystemExit):
        hook_allow("test message")
    out = json.loads(capsys.readouterr().out)
    assert out["systemMessage"] == "test message"

def test_hook_allow_empty_message(capsys):
    with pytest.raises(SystemExit):
        hook_allow()
    out = json.loads(capsys.readouterr().out)
    assert out == {}

def test_hook_block_exits_two():
    with pytest.raises(SystemExit) as exc:
        hook_block("blocked")
    assert exc.value.code == 2

def test_hook_block_writes_stderr(capsys):
    with pytest.raises(SystemExit):
        hook_block("blocked reason")
    assert "blocked reason" in capsys.readouterr().err

def test_hook_context_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        hook_context("context info")
    assert exc.value.code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["systemMessage"] == "context info"
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_hooks.py -v`
Expected: ImportError

- [ ] **Step 3: Implement hooks.py**

```python
# src/devlead/hooks.py
"""Hook output helpers for Claude Code integration.

Claude Code hooks use exit codes to control behavior:
- Exit 0: allow the action, optional JSON on stdout
- Exit 2: block the action, message on stderr
"""
import json
import sys

def hook_allow(message: str = "") -> None:
    output = {}
    if message:
        output["systemMessage"] = message
    print(json.dumps(output))
    sys.exit(0)

def hook_block(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(2)

def hook_context(context: str) -> None:
    print(json.dumps({"systemMessage": context}))
    sys.exit(0)
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_hooks.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/devlead/hooks.py tests/test_hooks.py
git commit -m "feat: hooks.py — hook output helpers (exit 0/2, JSON)"
```

---

## Task 2: state_machine.py — States, Transitions, Gates

**Files:**
- Create: `src/devlead/state_machine.py`
- Test: `tests/test_state_machine.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_state_machine.py
import json
import pytest
from pathlib import Path
from devlead.state_machine import (
    STATES, VALID_TRANSITIONS, GATE_ALLOWS, EXIT_CRITERIA,
    init_state, load_state, save_state,
    check_gate, do_transition, do_checklist, do_start,
)

def test_states_list():
    assert "SESSION_START" in STATES
    assert "ORIENT" in STATES
    assert "EXECUTE" in STATES
    assert len(STATES) == 7

def test_init_state_structure():
    state = init_state()
    assert state["state"] == "SESSION_START"
    assert "checklists" in state
    assert "ORIENT" in state["checklists"]
    assert "status_read" in state["checklists"]["ORIENT"]

def test_save_load_roundtrip(state_file):
    state = init_state()
    save_state(state, state_file)
    loaded = load_state(state_file)
    assert loaded["state"] == state["state"]
    assert loaded["checklists"] == state["checklists"]

def test_gate_allows_execute_in_execute(state_file):
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 0

def test_gate_blocks_execute_in_orient(state_file):
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 2

def test_gate_allows_edit_in_update(state_file):
    state = init_state()
    state["state"] = "UPDATE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 0

def test_gate_session_end_warns_not_blocks(state_file):
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "SESSION_END")
    assert exc.value.code == 0  # warn, not block

def test_gate_missing_state_file(state_file):
    with pytest.raises(SystemExit) as exc:
        check_gate(state_file, "EXECUTE")
    assert exc.value.code == 2

def test_transition_valid(state_file):
    state = init_state()
    state["state"] = "ORIENT"
    for key in state["checklists"]["ORIENT"]:
        state["checklists"]["ORIENT"][key] = True
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "INTAKE")
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "INTAKE"

def test_transition_invalid(state_file):
    state = init_state()
    state["state"] = "ORIENT"
    for key in state["checklists"]["ORIENT"]:
        state["checklists"]["ORIENT"][key] = True
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "EXECUTE")
    assert exc.value.code == 2

def test_transition_blocked_by_incomplete_checklist(state_file):
    state = init_state()
    state["state"] = "ORIENT"
    state["checklists"]["ORIENT"]["status_read"] = True
    # others remain False
    save_state(state, state_file)
    with pytest.raises(SystemExit) as exc:
        do_transition(state_file, "INTAKE")
    assert exc.value.code == 2

def test_checklist_marks_item(state_file):
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)
    do_checklist(state_file, "ORIENT", "status_read")
    loaded = load_state(state_file)
    assert loaded["checklists"]["ORIENT"]["status_read"] is True

def test_checklist_invalid_key(state_file):
    state = init_state()
    save_state(state, state_file)
    with pytest.raises(SystemExit):
        do_checklist(state_file, "ORIENT", "nonexistent_key")

def test_start_initializes_orient(state_file, tmp_docs):
    with pytest.raises(SystemExit) as exc:
        do_start(state_file, tmp_docs)
    assert exc.value.code == 0
    loaded = load_state(state_file)
    assert loaded["state"] == "ORIENT"
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_state_machine.py -v`
Expected: ImportError

- [ ] **Step 3: Implement state_machine.py**

See spec sections 6.1-6.8 for all constants. Key functions: `check_gate`, `do_transition`, `do_checklist`, `do_start`. All take `state_file: Path` as parameter (not module-level global). `do_start` creates ORIENT state and outputs hook context with basic status.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_state_machine.py -v`
Expected: 14 passed

- [ ] **Step 5: Wire into cli.py**

Add `start`, `gate`, `transition`, `checklist` commands to cli.py dispatch. Resolve `state_file` from cwd: `Path.cwd() / "claude_docs" / "session_state.json"`.

- [ ] **Step 6: Manual integration test**

```bash
mkdir -p /tmp/test_devlead/claude_docs && cd /tmp/test_devlead
devlead start       # outputs JSON, creates session_state.json
devlead gate EXECUTE  # exits 2 (we're in ORIENT)
```

- [ ] **Step 7: Commit**

```bash
git add src/devlead/state_machine.py src/devlead/cli.py tests/test_state_machine.py
git commit -m "feat: state machine — 7 states, transitions, gates, checklists"
```

---

## Task 3: config.py — TOML Configuration

**Files:**
- Create: `src/devlead/config.py`
- Create: `tests/fixtures/sample_devlead.toml`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing tests**

Test: defaults when no toml, loads toml, custom docs_dir, custom KPI formulas parsed, thresholds merge with defaults.

- [ ] **Step 2: Implement config.py**

Uses `tomllib` (stdlib 3.11+). `load_config(project_dir)` reads `devlead.toml`, merges with `DEFAULT_CONFIG`. Exports: `get_docs_dir()`, `get_state_file()`, `get_kpi_thresholds()`, `get_custom_kpis()`, `get_rollover_config()`.

- [ ] **Step 3: Run tests, verify pass**

Run: `python -m pytest tests/test_config.py -v`

- [ ] **Step 4: Wire config into cli.py and state_machine.py**

cli.py resolves all paths via config. state_machine functions receive config-derived paths.

- [ ] **Step 5: Commit**

```bash
git add src/devlead/config.py tests/test_config.py tests/fixtures/
git commit -m "feat: config.py — devlead.toml parsing with defaults"
```

---

## Task 4: doc_parser.py — Markdown Table Parsing

**Files:**
- Create: `src/devlead/doc_parser.py`
- Create: `tests/fixtures/_project_tasks.md` (10 tasks, mixed statuses)
- Create: `tests/fixtures/_project_roadmap.md` (5 stories with checkboxes)
- Create: `tests/fixtures/_intake_bugs.md` (3 bugs: 2 open, 1 closed)
- Create: `tests/fixtures/_intake_features.md` (2 features: 1 open, 1 closed)
- Create: `tests/fixtures/_intake_gaps.md` (1 gap, open)
- Create: `tests/fixtures/_project_status.md`
- Test: `tests/test_doc_parser.py`

- [ ] **Step 1: Create fixture files with KNOWN counts**

Task fixtures: 4 OPEN, 2 IN_PROGRESS, 3 DONE (1 REOPENED), 1 BLOCKED. 6 have story refs. 2 overdue.

- [ ] **Step 2: Write failing tests**

Test: `parse_table` returns list[dict] keyed by header. `count_by_status` returns correct counts. `count_with_pattern` finds story refs. `count_overdue`. `count_checkboxes`. `get_builtin_vars` returns all 18 variables with known values.

- [ ] **Step 3: Implement doc_parser.py**

Key: `parse_table(text)` finds header row (first row with `|`), extracts column names, maps each data row to dict. Parses by header name, not position.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_doc_parser.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/devlead/doc_parser.py tests/test_doc_parser.py tests/fixtures/
git commit -m "feat: doc_parser — markdown table parsing, builtin variables"
```

---

## Task 5: kpi_engine.py — 30 Built-in KPIs + Custom + Plugins

**Files:**
- Create: `src/devlead/kpi_engine.py`
- Create: `tests/fixtures/kpis/sample_plugin.py`
- Test: `tests/test_kpi_engine.py`

- [ ] **Step 1: Write failing tests for formula evaluator**

Test: simple arithmetic, variables, parentheses, division by zero returns 0, rejects function calls, rejects dunders.

- [ ] **Step 2: Implement safe formula evaluator**

Recursive descent parser. Tokenize into NUMBER, VARIABLE, OPERATOR, LPAREN, RPAREN. Parse with standard precedence (* / before + -). Variable lookup from dict. No `eval()`.

- [ ] **Step 3: Run formula tests, verify pass**

- [ ] **Step 4: Write failing tests for built-in KPIs**

Using Task 4 fixtures (known counts): test convergence, circles, FTR, intake throughput, doc freshness, coverage gap. Test dashboard format has A/B/C sections.

- [ ] **Step 5: Implement built-in KPIs**

`KpiResult` dataclass. `compute_builtin_kpis()` for all 23 single-project KPIs. `format_dashboard()` for terminal output.

- [ ] **Step 6: Write failing tests for custom TOML KPIs**

Test: formula evaluation with known variables, range clamping, warning thresholds.

- [ ] **Step 7: Implement custom KPI evaluation**

`compute_custom_kpis(custom_defs, vars)` — evaluates TOML formulas.

- [ ] **Step 8: Write failing tests for plugin KPIs**

Create `tests/fixtures/kpis/sample_plugin.py` with trivial `compute()`. Test: loads and runs, returns KpiResult.

- [ ] **Step 9: Implement plugin loading**

`load_plugin_kpi(module_path, vars, docs_dir)` — uses `importlib.util.spec_from_file_location`.

- [ ] **Step 10: Run all KPI tests**

Run: `python -m pytest tests/test_kpi_engine.py -v`

- [ ] **Step 11: Commit**

```bash
git add src/devlead/kpi_engine.py tests/test_kpi_engine.py tests/fixtures/kpis/
git commit -m "feat: KPI engine — 30 built-in, custom TOML, Python plugins"
```

---

## Task 6: Wire KPIs into CLI — `devlead status`, `devlead kpis`

**Files:**
- Modify: `src/devlead/state_machine.py` (do_start uses KPIs)
- Modify: `src/devlead/cli.py` (add status, kpis commands)
- Test: `tests/test_cli_integration.py`

- [ ] **Step 1: Write integration tests**

Test: `devlead start` outputs JSON with KPI data. `devlead status` shows state. `devlead kpis` shows dashboard. `devlead gate EXECUTE` exits 2 in ORIENT. Full lifecycle flow test.

- [ ] **Step 2: Wire KPIs into do_start**

`do_start()` calls `compute_all_kpis()`, formats dashboard, includes in hook_context.

- [ ] **Step 3: Add status and kpis commands to cli.py**

- [ ] **Step 4: Run integration tests**

Run: `python -m pytest tests/test_cli_integration.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/devlead/cli.py src/devlead/state_machine.py tests/test_cli_integration.py
git commit -m "feat: wire KPIs into CLI — status, kpis, start with dashboard"
```

---

## Task 7: scaffold/ + `devlead init`

**Files:**
- Create: `src/devlead/scaffold/claude_operatingmodel.md`
- Create: `src/devlead/scaffold/_living_standing_instructions.md`
- Create: `src/devlead/scaffold/_intake_bugs.md`
- Create: `src/devlead/scaffold/_intake_features.md`
- Create: `src/devlead/scaffold/_intake_gaps.md`
- Create: `src/devlead/scaffold/_intake_changes.md`
- Create: `src/devlead/scaffold/_project_status.md`
- Create: `src/devlead/scaffold/_project_tasks.md`
- Create: `src/devlead/scaffold/_project_roadmap.md`
- Create: `src/devlead/scaffold/hooks_settings.json`
- Create: `src/devlead/scaffold/devlead_toml_template.toml`
- Modify: `src/devlead/cli.py` (add init command)
- Test: `tests/test_init.py`

- [ ] **Step 1: Create scaffold template files**

Each `_intake_*.md` and `_project_*.md` has table headers matching spec section 8.3. `hooks_settings.json` matches spec section 6.4.

- [ ] **Step 2: Write failing tests**

Test: init creates claude_docs/ with all files, creates devlead.toml, merges hooks into .claude/settings.json (preserving existing), adds gitignore entry, idempotent skip on second run.

- [ ] **Step 3: Implement init command**

Copies scaffold files, merges hook JSON, appends to .gitignore. Handles existing files gracefully.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_init.py -v`

- [ ] **Step 5: Manual test**

```bash
cd /tmp && mkdir init_test && cd init_test && git init
devlead init
ls claude_docs/
cat devlead.toml
cat .claude/settings.json
```

- [ ] **Step 6: Commit**

```bash
git add src/devlead/scaffold/ src/devlead/cli.py tests/test_init.py
git commit -m "feat: devlead init — scaffold, hook config, gitignore"
```

---

## Task 8: rollover.py — Monthly Archival

**Files:**
- Create: `src/devlead/rollover.py`
- Modify: `src/devlead/cli.py` (add rollover command)
- Test: `tests/test_rollover.py`

- [ ] **Step 1: Write failing tests**

Test: creates archive dir, copies to archive with month suffix, carries forward open items, removes closed from current file, preserves header, idempotent same month, respects config files list.

- [ ] **Step 2: Implement rollover.py**

Uses `doc_parser.parse_table()` to identify open vs closed items. Copies full file to archive, rewrites current with only open items.

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_rollover.py -v`

- [ ] **Step 4: Commit**

```bash
git add src/devlead/rollover.py src/devlead/cli.py tests/test_rollover.py
git commit -m "feat: rollover — monthly archival with open item carry-forward"
```

---

## Task 9: doctor + Session History

**Files:**
- Modify: `src/devlead/cli.py` (add doctor command)
- Modify: `src/devlead/state_machine.py` (session history on SESSION_END)
- Modify: `src/devlead/kpi_engine.py` (LLM Learning Curve reads history)
- Test: `tests/test_doctor.py`
- Test: `tests/test_session_history.py`

- [ ] **Step 1: Write failing tests for doctor**

Test: all OK on complete scaffold, reports missing docs_dir, reports missing toml, reports empty intake.

- [ ] **Step 2: Implement doctor command**

Checks: claude_docs/ exists, devlead.toml found, .claude/settings.json has hooks, session_state.json in gitignore, all expected markdown files exist, tables have expected columns.

- [ ] **Step 3: Write failing tests for session history**

Test: transition to SESSION_END appends line to `session_history.jsonl`, line has expected schema.

- [ ] **Step 4: Implement session history**

On transition to SESSION_END: compute session metrics from state (circles from transition count, gate violations, etc.), append JSON line to `claude_docs/session_history.jsonl`.

- [ ] **Step 5: Wire LLM Learning Curve KPI to read history**

KPI #1 reads `session_history.jsonl`, compares rolling 5-session vs 10-session averages.

- [ ] **Step 6: Run all tests**

Run: `python -m pytest tests/test_doctor.py tests/test_session_history.py -v`

- [ ] **Step 7: Commit**

```bash
git add src/devlead/ tests/test_doctor.py tests/test_session_history.py
git commit -m "feat: doctor command + session history for LLM Learning Curve"
```

---

## Task 10: portfolio.py — Multi-Project Workspace (Pro)

**Files:**
- Create: `src/devlead/portfolio.py`
- Modify: `src/devlead/cli.py` (add portfolio commands)
- Test: `tests/test_portfolio.py`

- [ ] **Step 1: Write failing tests**

Test: add project to workspace.toml, remove project, list projects, portfolio KPIs (weighted convergence, weakest link), dashboard format.

- [ ] **Step 2: Implement portfolio.py**

`WORKSPACE_DIR = Path.home() / ".devlead"`. Functions: `add_project`, `remove_project`, `list_projects`, `compute_portfolio_kpis` (KPIs 24-30), `format_portfolio_dashboard`.

- [ ] **Step 3: Wire into cli.py**

Add `portfolio` subcommand with `add`, `remove`, `list` sub-subcommands. `devlead portfolio` (no sub) shows dashboard.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_portfolio.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/devlead/portfolio.py src/devlead/cli.py tests/test_portfolio.py
git commit -m "feat: portfolio — multi-project workspace, cross-project KPIs"
```

---

## Task 11: collab.py — Cross-Project Collaboration + Final Polish

**Files:**
- Create: `src/devlead/collab.py`
- Create: `tests/fixtures/collab/REQUEST_income_desk_001.md`
- Modify: `src/devlead/cli.py` (add collab commands)
- Modify: `src/devlead/state_machine.py` (ORIENT scans inbox)
- Test: `tests/test_collab.py`

- [ ] **Step 1: Write failing tests**

Test: init_collab creates dirs, parse_collab_file extracts metadata, scan_inbox finds requests, sync copies outbox to target inbox, collab_status shows open requests.

- [ ] **Step 2: Implement collab.py**

Functions: `init_collab`, `scan_inbox`, `sync_collab`, `collab_status`, `parse_collab_file`.

- [ ] **Step 3: Wire ORIENT to scan inbox**

In `do_start()`, if `.collab/INBOX/` exists, scan and report new requests.

- [ ] **Step 4: Wire collab KPIs**

KPI #25 (Cross-Project Blockers) and #30 (Collab Response Time) use collab data.

- [ ] **Step 5: Add collab commands to cli.py**

`devlead collab sync`, `devlead collab status`.

- [ ] **Step 6: Final polish**

- `devlead --help` lists all commands
- Error messages reference `devlead` consistently
- README.md (brief, points to docs/)

- [ ] **Step 7: Run FULL test suite**

```bash
python -m pytest tests/ -v
```

Expected: all tests pass across all modules.

- [ ] **Step 8: Full integration test**

```bash
cd /tmp && mkdir full_test && cd full_test && git init
devlead init
devlead doctor
devlead start
devlead checklist orient status_read
devlead checklist orient tasks_read
devlead checklist orient intake_scanned
devlead checklist orient kpis_reported
devlead transition INTAKE
devlead kpis
devlead rollover
devlead --version
```

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: collab channel + final polish — DevLead v0.1.0 complete"
```

---

## Verification Checklist

After all tasks complete:

- [ ] `pip install -e .` works
- [ ] `devlead --version` prints 0.1.0
- [ ] `devlead init` scaffolds complete project
- [ ] `devlead doctor` shows all OK on fresh init
- [ ] `devlead start` outputs KPI dashboard as hook JSON
- [ ] `devlead gate EXECUTE` blocks in ORIENT (exit 2)
- [ ] `devlead gate EXECUTE` allows in EXECUTE (exit 0)
- [ ] `devlead gate SESSION_END` warns, doesn't block (exit 0)
- [ ] Full state lifecycle completes: ORIENT → INTAKE → PLAN → EXECUTE → UPDATE → SESSION_END
- [ ] `devlead kpis` shows 30 KPIs across 3 categories
- [ ] Custom TOML KPIs compute correctly
- [ ] `devlead rollover` archives monthly
- [ ] `devlead portfolio add/list` manages workspace
- [ ] `devlead collab sync` copies between projects
- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Zero external dependencies confirmed

## Future (V2 Backlog)

- Token usage KPIs (read Claude Code transcript_path from hook input)
- Claude Workflow hooks (governance for scheduled/automated sessions)
- Cursor/Copilot hook adapters
- Web dashboard for KPI visualization
- CI/CD integration (fail build if KPIs below threshold)
- `devlead audit` — historical session analysis
