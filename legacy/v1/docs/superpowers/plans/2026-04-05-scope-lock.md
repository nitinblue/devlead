# Scope Lock + File Path Enforcement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users define exactly which files/directories the AI can touch during EXECUTE, and enforce it via the gate. Prevents the AI from wandering into wrong files or doing unrequested work.

**Architecture:** Scope is stored in `session_state.json` as a list of allowed paths (files or directories). The gate reads the file_path from hook stdin and checks it against scope. Scope only enforced during EXECUTE state — UPDATE state is unrestricted for doc updates. Scope auto-clears on transition out of EXECUTE.

**Tech Stack:** Python stdlib only (json, pathlib)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `src/devlead/scope.py` | Create | Scope management — set, show, clear, check |
| `src/devlead/state_machine.py` | Modify | Wire scope check into gate, auto-clear on transition |
| `src/devlead/config.py` | Modify | Add `[scope]` config section |
| `src/devlead/cli.py` | Modify | Add `scope` subcommand |
| `src/devlead/scaffold/devlead_toml_template.toml` | Modify | Add scope config |
| `tests/test_scope.py` | Create | Scope unit tests |
| `tests/test_scope_enforcement.py` | Create | Scope + gate integration tests |

---

## Task 1: scope.py — Scope Management

**Files:**
- Create: `src/devlead/scope.py`
- Test: `tests/test_scope.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scope.py
"""Tests for scope.py — scope lock management."""

import json
import pytest
from pathlib import Path
from devlead.scope import (
    set_scope,
    get_scope,
    clear_scope,
    is_in_scope,
)
from devlead.state_machine import init_state, save_state, load_state


def test_set_scope(state_file):
    """set_scope stores allowed paths in state."""
    state = init_state()
    state["state"] = "PLAN"
    save_state(state, state_file)

    set_scope(state_file, ["src/devlead/audit.py", "src/devlead/cli.py"])
    loaded = load_state(state_file)
    assert loaded["scope"] == ["src/devlead/audit.py", "src/devlead/cli.py"]


def test_set_scope_with_directories(state_file):
    """set_scope accepts directories."""
    state = init_state()
    state["state"] = "PLAN"
    save_state(state, state_file)

    set_scope(state_file, ["src/devlead/", "tests/"])
    loaded = load_state(state_file)
    assert "src/devlead/" in loaded["scope"]
    assert "tests/" in loaded["scope"]


def test_get_scope_empty(state_file):
    """get_scope returns empty list when no scope set."""
    state = init_state()
    save_state(state, state_file)
    assert get_scope(state_file) == []


def test_get_scope_set(state_file):
    """get_scope returns the scope list."""
    state = init_state()
    state["state"] = "PLAN"
    state["scope"] = ["src/main.py"]
    save_state(state, state_file)
    assert get_scope(state_file) == ["src/main.py"]


def test_clear_scope(state_file):
    """clear_scope removes scope from state."""
    state = init_state()
    state["scope"] = ["src/main.py"]
    save_state(state, state_file)

    clear_scope(state_file)
    loaded = load_state(state_file)
    assert loaded.get("scope", []) == []


def test_is_in_scope_no_scope():
    """No scope set = everything allowed."""
    assert is_in_scope("/project/src/main.py", [], "/project") is True


def test_is_in_scope_exact_file():
    """Exact file match."""
    scope = ["src/main.py"]
    assert is_in_scope("/project/src/main.py", scope, "/project") is True
    assert is_in_scope("/project/src/other.py", scope, "/project") is False


def test_is_in_scope_directory():
    """Directory scope allows all files under it."""
    scope = ["src/devlead/"]
    assert is_in_scope("/project/src/devlead/audit.py", scope, "/project") is True
    assert is_in_scope("/project/src/devlead/cli.py", scope, "/project") is True
    assert is_in_scope("/project/tests/test.py", scope, "/project") is False


def test_is_in_scope_multiple():
    """Multiple scope entries — any match allows."""
    scope = ["src/devlead/audit.py", "tests/"]
    assert is_in_scope("/project/src/devlead/audit.py", scope, "/project") is True
    assert is_in_scope("/project/tests/test_audit.py", scope, "/project") is True
    assert is_in_scope("/project/src/devlead/cli.py", scope, "/project") is False


def test_is_in_scope_absolute_path():
    """Works with absolute paths."""
    scope = ["src/main.py"]
    assert is_in_scope("C:/Users/nitin/project/src/main.py", scope, "C:/Users/nitin/project") is True


def test_is_in_scope_normalizes_slashes():
    """Handles mixed forward/back slashes."""
    scope = ["src/devlead/"]
    assert is_in_scope("C:\\project\\src\\devlead\\audit.py", scope, "C:\\project") is True
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_scope.py -v`
Expected: ImportError

- [ ] **Step 3: Implement scope.py**

```python
# src/devlead/scope.py
"""Scope lock — define and enforce which files the AI can touch.

Scope is stored in session_state.json. Only enforced during EXECUTE state.
Empty scope = everything allowed (backwards compatible).
"""

import json
from pathlib import Path, PurePosixPath


def set_scope(state_file: Path, paths: list[str]) -> None:
    """Set the allowed file/directory scope."""
    state = json.loads(state_file.read_text())
    state["scope"] = paths
    state_file.write_text(json.dumps(state, indent=2))


def get_scope(state_file: Path) -> list[str]:
    """Get the current scope. Returns [] if no scope set."""
    if not state_file.exists():
        return []
    state = json.loads(state_file.read_text())
    return state.get("scope", [])


def clear_scope(state_file: Path) -> None:
    """Remove scope lock."""
    if not state_file.exists():
        return
    state = json.loads(state_file.read_text())
    state["scope"] = []
    state_file.write_text(json.dumps(state, indent=2))


def is_in_scope(
    file_path: str,
    scope: list[str],
    project_dir: str,
) -> bool:
    """Check if a file_path is within the allowed scope.

    Returns True if:
    - scope is empty (no restriction)
    - file_path matches any scope entry (exact file or under directory)

    All paths normalized to forward slashes for comparison.
    """
    if not scope:
        return True

    # Normalize to forward slashes
    norm_file = file_path.replace("\\", "/")
    norm_project = project_dir.rstrip("/\\").replace("\\", "/")

    # Get relative path from project dir
    if norm_file.startswith(norm_project):
        rel_path = norm_file[len(norm_project):].lstrip("/")
    else:
        rel_path = norm_file

    for entry in scope:
        norm_entry = entry.replace("\\", "/")
        if norm_entry.endswith("/"):
            # Directory scope — check prefix
            if rel_path.startswith(norm_entry):
                return True
        else:
            # Exact file match
            if rel_path == norm_entry:
                return True

    return False
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_scope.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add src/devlead/scope.py tests/test_scope.py
git commit -m "feat: scope.py — scope lock management (set, get, clear, check)"
```

---

## Task 2: Wire Scope Into Gate Enforcement

**Files:**
- Modify: `src/devlead/state_machine.py`
- Test: `tests/test_scope_enforcement.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_scope_enforcement.py
"""Tests for scope enforcement in gate checks."""

import json
import pytest
from pathlib import Path
from devlead.state_machine import (
    check_gate_with_audit, init_state, save_state, load_state,
)
from devlead.scope import set_scope
from devlead.audit import read_audit_log


def test_scope_allows_in_scope_file(state_file, tmp_docs):
    """File in scope is allowed."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["scope"] = ["src/main.py"]
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "main.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 0


def test_scope_blocks_out_of_scope_file(state_file, tmp_docs):
    """File outside scope is blocked."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["scope"] = ["src/main.py"]
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "other.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 2


def test_scope_directory_allows_children(state_file, tmp_docs):
    """Directory scope allows files under it."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["scope"] = ["src/"]
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "deep" / "file.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 0


def test_no_scope_allows_everything(state_file, tmp_docs):
    """No scope set = allow all files."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "anything.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 0


def test_scope_not_enforced_in_update(state_file, tmp_docs):
    """Scope is NOT enforced in UPDATE state (docs need editing)."""
    state = init_state()
    state["state"] = "UPDATE"
    state["scope"] = ["src/main.py"]  # scope set but shouldn't matter in UPDATE
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "devlead_docs" / "_project_tasks.md")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 0


def test_scope_out_of_scope_logged_in_audit(state_file, tmp_docs):
    """Out-of-scope block is recorded in audit log."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["scope"] = ["src/allowed.py"]
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "forbidden.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 2

    records = read_audit_log(audit_log)
    assert len(records) == 1
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_scope_enforcement.py -v`
Expected: failures (scope check not wired yet)

- [ ] **Step 3: Wire scope check into check_gate_with_audit**

Update `check_gate_with_audit` in `src/devlead/state_machine.py`:

```python
def check_gate_with_audit(
    state_file: Path,
    gate: str,
    stdin_text: str,
    audit_log: Path,
) -> None:
    """Gate check with audit logging and scope enforcement.

    1. Parse hook stdin for file_path
    2. Log the write attempt to audit trail
    3. Check scope (only in EXECUTE state)
    4. Check state gate
    """
    from devlead.audit import parse_hook_stdin, log_write
    from devlead.scope import is_in_scope

    # Parse stdin for audit context
    entry = parse_hook_stdin(stdin_text) if stdin_text else None

    # Load current state
    current_state = ""
    scope = []
    if state_file.exists():
        state = load_state(state_file)
        current_state = state.get("state", "")
        scope = state.get("scope", [])

    # Log the write attempt
    if entry and entry.file_path:
        entry.state = current_state
        log_write(entry, audit_log)

    # Scope enforcement — only in EXECUTE state
    if (
        current_state == "EXECUTE"
        and scope
        and entry
        and entry.file_path
    ):
        if not is_in_scope(entry.file_path, scope, entry.cwd):
            hook_block(
                f"BLOCKED: File outside scope. "
                f"'{entry.file_path}' is not in allowed scope. "
                f"Use 'devlead scope show' to see allowed paths."
            )

    # Delegate to state gate check
    check_gate(state_file, gate)
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_scope_enforcement.py tests/test_scope.py -v`
Expected: all pass

- [ ] **Step 5: Run full suite**

Run: `python -m pytest tests/ -v`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add src/devlead/state_machine.py tests/test_scope_enforcement.py
git commit -m "feat: scope enforcement in gate — block file edits outside allowed scope"
```

---

## Task 3: Scope CLI + Auto-Clear on Transition

**Files:**
- Modify: `src/devlead/cli.py`
- Modify: `src/devlead/state_machine.py` (auto-clear scope on transition out of EXECUTE)
- Modify: `src/devlead/config.py`
- Modify: `src/devlead/scaffold/devlead_toml_template.toml`

- [ ] **Step 1: Add scope config to defaults**

Add to `DEFAULT_CONFIG` in `src/devlead/config.py`:

```python
    "scope": {
        "enforcement": "block",  # "log", "warn", "block"
        "auto_clear": True,      # clear scope on transition out of EXECUTE
    },
```

Add to `src/devlead/scaffold/devlead_toml_template.toml`:

```toml
[scope]
enforcement = "block"       # "log" = silent, "warn" = allow + warn, "block" = deny
auto_clear = true           # clear scope when leaving EXECUTE
```

- [ ] **Step 2: Add scope command to CLI**

Add `"scope"` to COMMANDS list.

Add to USAGE: `  scope         Set/show/clear file scope lock`

Add dispatch: `elif command == "scope": _cmd_scope(args[1:], state_file)`

Add handler:

```python
def _cmd_scope(sub_args: list[str], state_file: Path) -> None:
    """Manage scope lock."""
    from devlead.scope import set_scope, get_scope, clear_scope

    if not sub_args or sub_args[0] == "show":
        scope = get_scope(state_file)
        if not scope:
            print("No scope set. All files are editable during EXECUTE.")
        else:
            print("Scope lock active. Allowed paths:")
            for p in scope:
                print(f"  {p}")
    elif sub_args[0] == "set":
        if len(sub_args) < 2:
            print("Usage: devlead scope set <path1> [path2] ...", file=sys.stderr)
            sys.exit(1)
        set_scope(state_file, sub_args[1:])
        print(f"Scope set: {len(sub_args) - 1} path(s) allowed.")
        for p in sub_args[1:]:
            print(f"  {p}")
    elif sub_args[0] == "clear":
        clear_scope(state_file)
        print("Scope cleared. All files are editable during EXECUTE.")
    else:
        print(f"Unknown scope subcommand: {sub_args[0]}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 3: Auto-clear scope on transition out of EXECUTE**

In `do_transition` in `src/devlead/state_machine.py`, after the state is updated, add:

```python
    # Auto-clear scope when leaving EXECUTE
    if current == "EXECUTE" and "scope" in state:
        state["scope"] = []
```

(Insert before `save_state` and `hook_allow` at the end of do_transition)

- [ ] **Step 4: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/devlead/cli.py src/devlead/state_machine.py src/devlead/config.py src/devlead/scaffold/devlead_toml_template.toml
git commit -m "feat: devlead scope CLI + auto-clear on transition + configurable enforcement"
```

---

## Verification Checklist

- [ ] `devlead scope set src/main.py tests/` — sets scope
- [ ] `devlead scope show` — displays allowed paths
- [ ] `devlead scope clear` — removes scope
- [ ] Gate blocks edits to files outside scope during EXECUTE
- [ ] Gate allows edits to files inside scope during EXECUTE
- [ ] No scope = everything allowed (backwards compatible)
- [ ] Scope not enforced in UPDATE state
- [ ] Scope auto-clears on transition out of EXECUTE
- [ ] Out-of-scope blocks logged in audit trail
- [ ] `devlead.toml` `[scope]` section configures enforcement
- [ ] `python -m pytest tests/ -v` ��� all pass
- [ ] Zero external dependencies
