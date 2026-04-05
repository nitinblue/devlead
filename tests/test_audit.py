# tests/test_audit.py
"""Tests for audit.py — hook stdin parsing and write logging."""

import json
import pytest
from pathlib import Path
from datetime import datetime
from devlead.audit import (
    parse_hook_stdin,
    log_write,
    read_audit_log,
    AuditEntry,
)


def test_parse_hook_stdin_edit():
    """Parse Edit tool stdin JSON."""
    stdin_json = json.dumps({
        "session_id": "sess-123",
        "cwd": "/home/user/project",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/home/user/project/src/main.py",
            "old_string": "foo",
            "new_string": "bar",
        },
        "hook_event_name": "PreToolUse",
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.session_id == "sess-123"
    assert entry.cwd == "/home/user/project"
    assert entry.tool_name == "Edit"
    assert entry.file_path == "/home/user/project/src/main.py"


def test_parse_hook_stdin_write():
    """Parse Write tool stdin JSON."""
    stdin_json = json.dumps({
        "session_id": "sess-456",
        "cwd": "/home/user/project",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/home/user/project/new_file.py",
            "content": "print('hello')",
        },
        "hook_event_name": "PreToolUse",
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.tool_name == "Write"
    assert entry.file_path == "/home/user/project/new_file.py"


def test_parse_hook_stdin_with_agent():
    """Parse stdin with subagent context."""
    stdin_json = json.dumps({
        "session_id": "sess-789",
        "cwd": "/home/user/project",
        "tool_name": "Edit",
        "tool_input": {"file_path": "/tmp/file.py"},
        "agent_id": "agent-abc",
        "agent_type": "Explore",
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.agent_id == "agent-abc"
    assert entry.agent_type == "Explore"


def test_parse_hook_stdin_no_file_path():
    """Non-file tools return None file_path."""
    stdin_json = json.dumps({
        "session_id": "sess-000",
        "cwd": "/home/user/project",
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.file_path is None


def test_parse_hook_stdin_bad_json():
    """Malformed JSON returns None."""
    entry = parse_hook_stdin("not json at all")
    assert entry is None


def test_log_write(tmp_path):
    """log_write appends a JSONL line to audit log."""
    log_file = tmp_path / "_audit_log.jsonl"
    entry = AuditEntry(
        session_id="sess-123",
        cwd="/project",
        tool_name="Edit",
        file_path="/project/src/main.py",
        state="EXECUTE",
    )
    log_write(entry, log_file)
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["session_id"] == "sess-123"
    assert record["file_path"] == "/project/src/main.py"
    assert record["state"] == "EXECUTE"
    assert "timestamp" in record


def test_log_write_appends(tmp_path):
    """Multiple log_write calls append, not overwrite."""
    log_file = tmp_path / "_audit_log.jsonl"
    for i in range(3):
        entry = AuditEntry(
            session_id=f"sess-{i}",
            cwd="/project",
            tool_name="Edit",
            file_path=f"/project/file{i}.py",
            state="EXECUTE",
        )
        log_write(entry, log_file)
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 3


def test_log_write_cross_project(tmp_path):
    """Cross-project write is flagged in log."""
    log_file = tmp_path / "_audit_log.jsonl"
    entry = AuditEntry(
        session_id="sess-123",
        cwd="/project_a",
        tool_name="Edit",
        file_path="/project_b/src/other.py",
        state="EXECUTE",
    )
    log_write(entry, log_file)
    record = json.loads(log_file.read_text().strip())
    assert record["cross_project"] is True


def test_read_audit_log(tmp_path):
    """read_audit_log returns list of dicts."""
    log_file = tmp_path / "_audit_log.jsonl"
    entry = AuditEntry(
        session_id="sess-1",
        cwd="/project",
        tool_name="Edit",
        file_path="/project/f.py",
        state="EXECUTE",
    )
    log_write(entry, log_file)
    records = read_audit_log(log_file)
    assert len(records) == 1
    assert records[0]["session_id"] == "sess-1"


def test_read_audit_log_missing(tmp_path):
    """Missing log file returns empty list."""
    log_file = tmp_path / "_audit_log.jsonl"
    records = read_audit_log(log_file)
    assert records == []
