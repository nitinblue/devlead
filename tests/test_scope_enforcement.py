"""Tests for scope enforcement in gate checks."""

import json
import pytest
from pathlib import Path
from devlead.state_machine import (
    check_gate_with_audit, init_state, save_state, load_state,
)
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


def test_scope_warns_out_of_scope_default(state_file, tmp_docs, capsys):
    """Default posture: out-of-scope file is ALLOWED but logged (warn via context)."""
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
    # Default enforcement is "log" — allows but logs
    assert exc.value.code == 0


def test_scope_blocks_when_configured(state_file, tmp_docs):
    """Block enforcement: out-of-scope file is blocked."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["scope"] = ["src/main.py"]
    state["scope_enforcement"] = "block"
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
    """Scope is NOT enforced in UPDATE state."""
    state = init_state()
    state["state"] = "UPDATE"
    state["scope"] = ["src/main.py"]
    state["scope_enforcement"] = "block"  # even with block, UPDATE is free
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "claude_docs" / "_project_tasks.md")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 0


def test_scope_out_of_scope_logged_in_audit(state_file, tmp_docs):
    """Out-of-scope access is recorded in audit log regardless of enforcement."""
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
    # Default is "log" so it allows
    assert exc.value.code == 0

    records = read_audit_log(audit_log)
    assert len(records) == 1
