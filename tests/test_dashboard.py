"""Tests for dashboard.py — HTML session report generation."""

import json
import shutil
from pathlib import Path
from datetime import date, datetime

import pytest

from devlead.dashboard import generate_dashboard_html, write_dashboard


FIXTURES = Path(__file__).parent / "fixtures"


def _setup_project(tmp_path: Path) -> Path:
    """Set up a project with fixtures, state, and audit log."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    # Create session state
    state = {
        "state": "UPDATE",
        "session_start": "2026-04-05T10:00:00+00:00",
        "transitions": [
            {"from": "SESSION_START", "to": "ORIENT", "at": "2026-04-05T10:00:01+00:00"},
            {"from": "ORIENT", "to": "INTAKE", "at": "2026-04-05T10:05:00+00:00"},
            {"from": "INTAKE", "to": "PLAN", "at": "2026-04-05T10:10:00+00:00"},
            {"from": "PLAN", "to": "EXECUTE", "at": "2026-04-05T10:15:00+00:00"},
            {"from": "EXECUTE", "to": "UPDATE", "at": "2026-04-05T11:30:00+00:00"},
        ],
        "checklists": {
            "ORIENT": {"status_read": True, "tasks_read": True, "intake_scanned": True, "kpis_reported": True},
            "INTAKE": {"requests_captured": True, "triaged": True},
            "UPDATE": {"intake_updated": False, "tasks_updated": True, "status_updated": False, "living_reviewed": False, "memory_derived": False},
        },
        "scope": ["src/devlead/", "tests/"],
    }
    (docs / "session_state.json").write_text(json.dumps(state))

    # Create audit log
    audit = docs / "_audit_log.jsonl"
    entries = [
        {"timestamp": "2026-04-05T10:20:00", "session_id": "sess-1", "cwd": str(tmp_path), "tool_name": "Edit", "file_path": str(tmp_path / "src" / "main.py"), "state": "EXECUTE", "cross_project": False},
        {"timestamp": "2026-04-05T10:25:00", "session_id": "sess-1", "cwd": str(tmp_path), "tool_name": "Write", "file_path": str(tmp_path / "src" / "new.py"), "state": "EXECUTE", "cross_project": False},
        {"timestamp": "2026-04-05T10:30:00", "session_id": "sess-1", "cwd": str(tmp_path), "tool_name": "Edit", "file_path": "/other/project/file.py", "state": "EXECUTE", "cross_project": True},
    ]
    audit.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

    return tmp_path


def test_generate_dashboard_html(tmp_path):
    """Dashboard generates valid HTML."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "<!DOCTYPE html>" in html
    assert "DevLead" in html
    assert "</html>" in html


def test_dashboard_contains_kpis(tmp_path):
    """Dashboard includes KPI section."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "LLM EFFECTIVENESS" in html or "LLM Effectiveness" in html
    assert "Delivery" in html or "DELIVERY" in html
    assert "Project Health" in html or "PROJECT HEALTH" in html


def test_dashboard_contains_state_timeline(tmp_path):
    """Dashboard includes state transition timeline."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "ORIENT" in html
    assert "EXECUTE" in html
    assert "UPDATE" in html


def test_dashboard_contains_audit_log(tmp_path):
    """Dashboard includes audit entries."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "main.py" in html
    assert "CROSS" in html or "cross" in html


def test_dashboard_contains_project_stats(tmp_path):
    """Dashboard includes task/story/intake counts."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "tasks" in html.lower() or "Tasks" in html
    assert "stories" in html.lower() or "Stories" in html


def test_dashboard_contains_checklist_status(tmp_path):
    """Dashboard shows checklist completion."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "status_read" in html or "Checklist" in html


def test_dashboard_contains_scope(tmp_path):
    """Dashboard shows scope if set."""
    project = _setup_project(tmp_path)
    html = generate_dashboard_html(project, today=date(2026, 4, 5))
    assert "scope" in html.lower() or "src/devlead/" in html


def test_write_dashboard(tmp_path):
    """write_dashboard creates an HTML file."""
    project = _setup_project(tmp_path)
    path = write_dashboard(project, today=date(2026, 4, 5))
    assert path.exists()
    assert path.suffix == ".html"
    content = path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_write_dashboard_filename(tmp_path):
    """Dashboard filename includes date."""
    project = _setup_project(tmp_path)
    path = write_dashboard(project, today=date(2026, 4, 5))
    assert "2026-04-05" in path.name


def test_dashboard_no_state_file(tmp_path):
    """Dashboard works even without session state."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)
    html = generate_dashboard_html(tmp_path, today=date(2026, 4, 5))
    assert "<!DOCTYPE html>" in html


def test_dashboard_empty_project(tmp_path):
    """Dashboard works on empty project."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    html = generate_dashboard_html(tmp_path, today=date(2026, 4, 5))
    assert "<!DOCTYPE html>" in html
