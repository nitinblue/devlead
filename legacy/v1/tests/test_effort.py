# tests/test_effort.py
"""Tests for effort.py — task effort recording and aggregation."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta

from devlead.effort import (
    record_task_effort,
    get_task_effort,
    get_story_effort,
)


def _write_tasks_md(docs_dir: Path, rows: list[tuple[str, str, str]]) -> None:
    """Helper: write a minimal _project_tasks.md with (ID, Story, Status) rows."""
    lines = [
        "# Tasks\n",
        "| ID | Task | Story | Priority | Status | Assignee |",
        "|----|------|-------|----------|--------|----------|",
    ]
    for tid, story, status in rows:
        lines.append(f"| {tid} | desc | {story} | P1 | {status} | AI |")
    (docs_dir / "_project_tasks.md").write_text("\n".join(lines), encoding="utf-8")


def test_record_task_effort(tmp_path):
    """record_task_effort writes a JSONL entry."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    record_task_effort(docs_dir, "TASK-001", tokens=500, session_id="sess-1")

    log_file = docs_dir / "_effort_log.jsonl"
    assert log_file.exists()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["task_id"] == "TASK-001"
    assert entry["tokens"] == 500
    assert entry["session_id"] == "sess-1"
    assert "timestamp" in entry


def test_record_task_effort_appends(tmp_path):
    """Multiple calls append to the log."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    record_task_effort(docs_dir, "TASK-001", tokens=100, session_id="s1")
    record_task_effort(docs_dir, "TASK-001", tokens=200, session_id="s2")
    record_task_effort(docs_dir, "TASK-002", tokens=300, session_id="s1")

    log_file = docs_dir / "_effort_log.jsonl"
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 3


def test_record_task_effort_reads_session_state(tmp_path):
    """Session ID is read from session_state.json when not provided."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()
    state_file = docs_dir / "session_state.json"
    state_file.write_text(json.dumps({"session_id": "from-state"}))

    record_task_effort(docs_dir, "TASK-001", tokens=50)

    log_file = docs_dir / "_effort_log.jsonl"
    entry = json.loads(log_file.read_text().strip())
    assert entry["session_id"] == "from-state"


def test_get_task_effort(tmp_path):
    """get_task_effort aggregates tokens and sessions correctly."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    record_task_effort(docs_dir, "TASK-010", tokens=100, session_id="s1")
    record_task_effort(docs_dir, "TASK-010", tokens=250, session_id="s1")
    record_task_effort(docs_dir, "TASK-010", tokens=150, session_id="s2")
    # Different task — should not be counted
    record_task_effort(docs_dir, "TASK-099", tokens=9999, session_id="s3")

    result = get_task_effort(docs_dir, "TASK-010")
    assert result["total_tokens"] == 500
    assert result["session_count"] == 2
    assert result["first_seen"] != ""
    assert result["last_seen"] != ""
    assert result["duration_estimate"] >= 0


def test_get_task_effort_duration(tmp_path):
    """Duration estimate is computed from first/last timestamps."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    # Write entries manually with controlled timestamps
    log_file = docs_dir / "_effort_log.jsonl"
    t0 = datetime(2026, 4, 5, 10, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(hours=2)
    entries = [
        {"task_id": "TASK-020", "timestamp": t0.isoformat(), "tokens": 100, "session_id": "s1"},
        {"task_id": "TASK-020", "timestamp": t1.isoformat(), "tokens": 200, "session_id": "s1"},
    ]
    with open(log_file, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    result = get_task_effort(docs_dir, "TASK-020")
    assert result["total_tokens"] == 300
    assert result["duration_estimate"] == 7200  # 2 hours in seconds


def test_get_story_effort(tmp_path):
    """get_story_effort aggregates across child tasks."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    _write_tasks_md(docs_dir, [
        ("TASK-001", "S-005", "IN_PROGRESS"),
        ("TASK-002", "S-005", "DONE"),
        ("TASK-003", "S-006", "IN_PROGRESS"),
    ])

    record_task_effort(docs_dir, "TASK-001", tokens=100, session_id="s1")
    record_task_effort(docs_dir, "TASK-002", tokens=200, session_id="s1")
    record_task_effort(docs_dir, "TASK-002", tokens=300, session_id="s2")
    # Task from different story — should not be counted
    record_task_effort(docs_dir, "TASK-003", tokens=999, session_id="s3")

    result = get_story_effort(docs_dir, "S-005")
    assert result["total_tokens"] == 600
    assert result["session_count"] == 2  # s1 and s2
    assert result["task_count"] == 2  # TASK-001 and TASK-002


def test_effort_no_log(tmp_path):
    """Returns zeros when no effort log exists."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    result = get_task_effort(docs_dir, "TASK-999")
    assert result["total_tokens"] == 0
    assert result["session_count"] == 0
    assert result["first_seen"] == ""
    assert result["last_seen"] == ""
    assert result["duration_estimate"] == 0


def test_story_effort_no_log(tmp_path):
    """get_story_effort returns zeros when no log exists."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    _write_tasks_md(docs_dir, [("TASK-001", "S-001", "OPEN")])

    result = get_story_effort(docs_dir, "S-001")
    assert result["total_tokens"] == 0
    assert result["session_count"] == 0
    assert result["task_count"] == 0


def test_story_effort_no_tasks_file(tmp_path):
    """get_story_effort returns zeros when tasks file is missing."""
    docs_dir = tmp_path / "devlead_docs"
    docs_dir.mkdir()

    result = get_story_effort(docs_dir, "S-001")
    assert result["total_tokens"] == 0
    assert result["session_count"] == 0
    assert result["task_count"] == 0
