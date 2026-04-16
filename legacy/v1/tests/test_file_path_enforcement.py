"""Tests for file path enforcement — memory writes and devlead_docs protection."""

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
    save_state(state, state_file)

    memory_path = str(Path.home() / ".claude" / "projects" / "test" / "memory" / "note.md")
    stdin = _make_stdin(str(tmp_docs.parent), memory_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 2


def test_memory_write_blocked_in_execute_default(state_file, tmp_docs, capsys):
    """Memory writes are blocked in EXECUTE by default (governance: block)."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    memory_path = str(Path.home() / ".claude" / "projects" / "test" / "memory" / "note.md")
    stdin = _make_stdin(str(tmp_docs.parent), memory_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    # block = exit 2
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "memory" in err.lower() or "UPDATE" in err


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


# --- devlead_docs protection ---

def test_devlead_docs_write_allowed_in_update(state_file, tmp_docs):
    """devlead_docs writes are allowed in UPDATE state."""
    state = init_state()
    state["state"] = "UPDATE"
    save_state(state, state_file)

    docs_path = str(tmp_docs / "_project_tasks.md")
    stdin = _make_stdin(str(tmp_docs.parent), docs_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 0


def test_devlead_docs_write_warned_in_execute(state_file, tmp_docs, capsys):
    """devlead_docs writes get warned in EXECUTE by default."""
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
    assert "devlead_docs" in out or "UPDATE" in out


def test_devlead_docs_write_blocked_when_configured(state_file, tmp_docs):
    """devlead_docs writes blocked in EXECUTE when policy is block."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    # Configure docs_policy=block via devlead.toml
    project_dir = tmp_docs.parent
    (project_dir / "devlead.toml").write_text(
        '[[gates]]\nname = "protect-docs"\ntrigger = "Edit|Write"\n'
        'path = "**/devlead_docs/**"\n'
        'condition = "state_not_in(UPDATE, SESSION_END)"\n'
        'action = "block"\n'
        'message = "docs blocked"\n',
        encoding="utf-8",
    )

    docs_path = str(tmp_docs / "_project_tasks.md")
    stdin = _make_stdin(str(project_dir), docs_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 2


def test_normal_file_unaffected(state_file, tmp_docs):
    """Normal source files are not affected by memory/docs policies."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    src_path = str(tmp_docs.parent / "src" / "main.py")
    stdin = _make_stdin(str(tmp_docs.parent), src_path)
    audit_log = tmp_docs / "_audit_log.jsonl"

    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin, audit_log)
    assert exc.value.code == 0
