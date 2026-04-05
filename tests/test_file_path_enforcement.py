"""Tests for file path enforcement — memory writes and claude_docs protection."""

import json
import pytest
from pathlib import Path
from devlead.state_machine import (
    check_gate_with_audit, init_state, save_state,
)
from devlead.audit import read_audit_log


def _make_stdin(cwd, file_path):
    return json.dumps({
        "session_id": "sess-1",
        "cwd": cwd,
        "tool_name": "Write",
        "tool_input": {"file_path": file_path},
    })


# --- Memory path detection ---

def test_memory_write_allowed_in_update(state_file, tmp_docs):
    """Memory writes are allowed in UPDATE state."""
    state = init_state()
    state["state"] = "UPDATE"
    save_state(state, state_file)

    memory_path = str(Path.home() / ".claude" / "projects" / "test" / "memory" / "note.md")
    stdin = _make_stdin(str(tmp_docs.parent), memory_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 0


def test_memory_write_blocked_in_execute(state_file, tmp_docs):
    """Memory writes are blocked in EXECUTE state (default: warn)."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["memory_policy"] = "block"
    save_state(state, state_file)

    memory_path = str(Path.home() / ".claude" / "projects" / "test" / "memory" / "note.md")
    stdin = _make_stdin(str(tmp_docs.parent), memory_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 2


def test_memory_write_warned_in_execute_default(state_file, tmp_docs, capsys):
    """Memory writes get warn (allow + context) in EXECUTE by default."""
    state = init_state()
    state["state"] = "EXECUTE"
    # default memory_policy = "warn"
    save_state(state, state_file)

    memory_path = str(Path.home() / ".claude" / "projects" / "test" / "memory" / "note.md")
    stdin = _make_stdin(str(tmp_docs.parent), memory_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    # warn = allow (exit 0) but with context message
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "memory" in out.lower() or "UPDATE" in out


def test_memory_write_logged_in_audit(state_file, tmp_docs):
    """Memory writes always appear in audit log."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    memory_path = str(Path.home() / ".claude" / "projects" / "test" / "memory" / "note.md")
    stdin = _make_stdin(str(tmp_docs.parent), memory_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit):
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)

    records = read_audit_log(audit_log)
    assert len(records) == 1
    assert "memory" in records[0]["file_path"].lower() or ".claude" in records[0]["file_path"]


# --- claude_docs protection ---

def test_claude_docs_write_allowed_in_update(state_file, tmp_docs):
    """claude_docs writes are allowed in UPDATE state."""
    state = init_state()
    state["state"] = "UPDATE"
    save_state(state, state_file)

    docs_path = str(tmp_docs / "_project_tasks.md")
    stdin = _make_stdin(str(tmp_docs.parent), docs_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 0


def test_claude_docs_write_warned_in_execute(state_file, tmp_docs, capsys):
    """claude_docs writes get warned in EXECUTE by default."""
    state = init_state()
    state["state"] = "EXECUTE"
    # default docs_policy = "warn"
    save_state(state, state_file)

    docs_path = str(tmp_docs / "_project_tasks.md")
    stdin = _make_stdin(str(tmp_docs.parent), docs_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "claude_docs" in out or "UPDATE" in out


def test_claude_docs_write_blocked_when_configured(state_file, tmp_docs):
    """claude_docs writes blocked in EXECUTE when policy is block."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["docs_policy"] = "block"
    save_state(state, state_file)

    docs_path = str(tmp_docs / "_project_tasks.md")
    stdin = _make_stdin(str(tmp_docs.parent), docs_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 2


def test_normal_file_unaffected(state_file, tmp_docs):
    """Normal source files are not affected by memory/docs policies."""
    state = init_state()
    state["state"] = "EXECUTE"
    state["memory_policy"] = "block"
    state["docs_policy"] = "block"
    save_state(state, state_file)

    src_path = str(tmp_docs.parent / "src" / "main.py")
    stdin = _make_stdin(str(tmp_docs.parent), src_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 0
