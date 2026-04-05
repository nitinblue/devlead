"""Tests for audit integration with gate checks."""

import json
import pytest
from pathlib import Path
from devlead.state_machine import check_gate_with_audit, load_state, save_state, init_state
from devlead.audit import read_audit_log


def test_gate_logs_edit_to_audit(state_file, tmp_docs):
    """Gate check logs the file write to audit log."""
    state = init_state()
    state["state"] = "EXECUTE"
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

    records = read_audit_log(audit_log)
    assert len(records) == 1
    assert records[0]["state"] == "EXECUTE"
    assert "main.py" in records[0]["file_path"]


def test_gate_logs_blocked_write(state_file, tmp_docs):
    """Blocked writes are also logged."""
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-2",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "file.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 2

    records = read_audit_log(audit_log)
    assert len(records) == 1
    assert records[0]["state"] == "ORIENT"


def test_gate_no_stdin_still_works(state_file, tmp_docs):
    """Gate works without stdin (backwards compat)."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", "", audit_log)
    assert exc.value.code == 0
