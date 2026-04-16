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
