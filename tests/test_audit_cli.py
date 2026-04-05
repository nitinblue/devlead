"""Tests for devlead audit CLI command."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "devlead"] + args,
        capture_output=True, text=True, cwd=str(cwd),
    )


def test_audit_show_empty(tmp_path):
    """devlead audit shows empty when no log."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    result = _run(["audit"], cwd=tmp_path)
    assert result.returncode == 0
    assert "No audit entries" in result.stdout


def test_audit_show_entries(tmp_path):
    """devlead audit shows logged entries."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    log = docs / "_audit_log.jsonl"
    log.write_text(json.dumps({
        "timestamp": "2026-04-05T10:00:00",
        "session_id": "sess-1",
        "cwd": str(tmp_path),
        "tool_name": "Edit",
        "file_path": str(tmp_path / "src" / "main.py"),
        "state": "EXECUTE",
        "cross_project": False,
    }) + "\n")
    result = _run(["audit"], cwd=tmp_path)
    assert result.returncode == 0
    assert "Edit" in result.stdout
    assert "main.py" in result.stdout


def test_audit_cross_project_flag(tmp_path):
    """devlead audit highlights cross-project writes."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    log = docs / "_audit_log.jsonl"
    log.write_text(json.dumps({
        "timestamp": "2026-04-05T10:00:00",
        "session_id": "sess-1",
        "cwd": "/project_a",
        "tool_name": "Edit",
        "file_path": "/project_b/file.py",
        "state": "EXECUTE",
        "cross_project": True,
    }) + "\n")
    result = _run(["audit"], cwd=tmp_path)
    assert "CROSS" in result.stdout
