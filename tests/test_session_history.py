"""Tests for session_history.py — capture session snapshots for trend tracking."""

import json
import shutil
from pathlib import Path
from datetime import date

import pytest

from devlead.session_history import (
    capture_session_snapshot,
    read_session_history,
    compute_deltas,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _setup_project(tmp_path: Path) -> Path:
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)
    return docs


def test_capture_snapshot(tmp_path):
    """Capture writes a JSONL line with all metrics."""
    docs = _setup_project(tmp_path)
    history_file = docs / "session_history.jsonl"

    state = {
        "state": "UPDATE",
        "transitions": [
            {"from": "SESSION_START", "to": "ORIENT", "at": "2026-04-05T10:00:00"},
            {"from": "ORIENT", "to": "INTAKE", "at": "2026-04-05T10:05:00"},
            {"from": "INTAKE", "to": "PLAN", "at": "2026-04-05T10:10:00"},
            {"from": "PLAN", "to": "EXECUTE", "at": "2026-04-05T10:15:00"},
            {"from": "EXECUTE", "to": "UPDATE", "at": "2026-04-05T11:30:00"},
        ],
    }

    capture_session_snapshot(docs, state, history_file, today=date(2026, 4, 5))

    lines = history_file.read_text().strip().splitlines()
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["date"] == "2026-04-05"
    assert record["transitions"] == 5
    assert "tasks_total" in record
    assert "tasks_done" in record
    assert "convergence" in record
    assert "epics_total" in record
    assert "stories_done" in record
    assert "intake_open" in record


def test_capture_appends(tmp_path):
    """Multiple captures append, not overwrite."""
    docs = _setup_project(tmp_path)
    history_file = docs / "session_history.jsonl"
    state = {"state": "UPDATE", "transitions": []}

    capture_session_snapshot(docs, state, history_file, today=date(2026, 4, 5))
    capture_session_snapshot(docs, state, history_file, today=date(2026, 4, 6))

    lines = history_file.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["date"] == "2026-04-05"
    assert json.loads(lines[1])["date"] == "2026-04-06"


def test_read_session_history(tmp_path):
    """read_session_history returns list of dicts."""
    docs = _setup_project(tmp_path)
    history_file = docs / "session_history.jsonl"
    state = {"state": "UPDATE", "transitions": []}
    capture_session_snapshot(docs, state, history_file, today=date(2026, 4, 5))

    records = read_session_history(history_file)
    assert len(records) == 1
    assert records[0]["date"] == "2026-04-05"


def test_read_session_history_missing(tmp_path):
    """Missing file returns empty list."""
    records = read_session_history(tmp_path / "nope.jsonl")
    assert records == []


def test_compute_deltas_first_session():
    """First session has no deltas — returns empty dict."""
    history = [{"date": "2026-04-05", "tasks_done": 3, "convergence": 40}]
    deltas = compute_deltas(history)
    assert deltas == {}


def test_compute_deltas_two_sessions():
    """Deltas computed between last two sessions."""
    history = [
        {"date": "2026-04-04", "tasks_done": 2, "convergence": 30, "intake_open": 5, "tasks_total": 8},
        {"date": "2026-04-05", "tasks_done": 5, "convergence": 40, "intake_open": 3, "tasks_total": 10},
    ]
    deltas = compute_deltas(history)
    assert deltas["tasks_done"] == 3  # 5 - 2
    assert deltas["convergence"] == 10  # 40 - 30
    assert deltas["intake_open"] == -2  # 3 - 5 (good — backlog shrinking)
    assert deltas["tasks_total"] == 2


def test_compute_deltas_ignores_non_numeric():
    """Non-numeric fields (date, state) are skipped."""
    history = [
        {"date": "2026-04-04", "state": "UPDATE", "tasks_done": 2},
        {"date": "2026-04-05", "state": "SESSION_END", "tasks_done": 5},
    ]
    deltas = compute_deltas(history)
    assert "date" not in deltas
    assert "state" not in deltas
    assert deltas["tasks_done"] == 3
