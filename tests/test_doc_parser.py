"""Tests for doc_parser.py — markdown table parsing and builtin variables.

Fixture counts (known values):
- _project_tasks.md: 10 tasks total
  - 3 OPEN (TASK-004, 005, 006), 2 IN_PROGRESS (003, 009), 3 DONE (001, 002, 010)
  - 1 REOPENED (007), 1 BLOCKED (008)
  - tasks_with_story: 8 (all except 006 and 008)
  - tasks_overdue: 2 (TASK-004 due 04-01, TASK-007 due 03-30 — both before 04-05)
  - tasks_active: OPEN + IN_PROGRESS + REOPENED + BLOCKED = 3+2+1+1 = 7
- _project_roadmap.md: 5 stories, 2 done ([x])
- _intake_bugs.md: 3 items (2 open, 1 closed)
- _intake_features.md: 2 items (1 open, 1 closed)
- _intake_gaps.md: 1 item (1 open, 0 closed)
- intake totals: 6 total, 4 open, 2 closed
"""

import pytest
from pathlib import Path
from datetime import date
from devlead.doc_parser import (
    parse_table,
    count_by_status,
    count_with_pattern,
    count_overdue,
    count_checkboxes,
    get_builtin_vars,
)


FIXTURES = Path(__file__).parent / "fixtures"


# --- parse_table ---

def test_parse_table_returns_list_of_dicts():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert isinstance(rows, list)
    assert len(rows) == 10
    assert isinstance(rows[0], dict)


def test_parse_table_keys_from_headers():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert "ID" in rows[0]
    assert "Task" in rows[0]
    assert "Status" in rows[0]
    assert "Story" in rows[0]


def test_parse_table_values():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    first = rows[0]
    assert first["ID"].strip() == "TASK-001"
    assert "DONE" in first["Status"]


def test_parse_table_empty():
    """Table with only headers and separator returns empty list."""
    text = "| A | B |\n|---|---|\n"
    rows = parse_table(text)
    assert rows == []


def test_parse_table_no_table():
    """Text with no table returns empty list."""
    rows = parse_table("# Just a heading\n\nSome text.\n")
    assert rows == []


# --- count_by_status ---

def test_count_open():
    """OPEN matches 3 OPEN + 1 REOPENED (contains "OPEN") = 4."""
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_by_status(rows, "OPEN") == 4


def test_count_done():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_by_status(rows, "DONE") == 3


def test_count_in_progress():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_by_status(rows, "IN_PROGRESS") == 2


def test_count_blocked():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_by_status(rows, "BLOCKED") == 1


def test_count_reopened():
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_by_status(rows, "REOPEN") == 1


# --- count_with_pattern ---

def test_count_with_story_ref():
    """8 tasks have S-NNN or E-NNN in Story column."""
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_with_pattern(rows, "Story", r"[SE]-\d+") == 8


# --- count_overdue ---

def test_count_overdue():
    """2 tasks overdue as of 2026-04-05."""
    text = (FIXTURES / "_project_tasks.md").read_text()
    rows = parse_table(text)
    assert count_overdue(rows, "Due", today=date(2026, 4, 5)) == 2


def test_count_overdue_no_due_column():
    """Rows without Due column return 0."""
    rows = [{"ID": "1", "Status": "OPEN"}]
    assert count_overdue(rows, "Due") == 0


# --- count_checkboxes ---

def test_count_checkboxes_done():
    text = (FIXTURES / "_project_roadmap.md").read_text()
    done, total = count_checkboxes(text)
    assert done == 2
    assert total == 5


def test_count_checkboxes_none():
    done, total = count_checkboxes("# No checkboxes here\n\nJust text.\n")
    assert done == 0
    assert total == 0


# --- get_builtin_vars ---

def test_builtin_vars_tasks(tmp_path):
    """Builtin vars computed from fixture docs."""
    # Copy fixtures to tmp_path so get_builtin_vars can find them
    _copy_fixtures_to(tmp_path)
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))

    assert vars["tasks_open"] == 4  # 3 OPEN + 1 REOPENED (contains "OPEN")
    assert vars["tasks_in_progress"] == 2
    assert vars["tasks_done"] == 3
    assert vars["tasks_total"] == 10
    assert vars["tasks_blocked"] == 1
    assert vars["tasks_reopened"] == 1
    assert vars["tasks_overdue"] == 2
    assert vars["tasks_with_story"] == 8
    assert vars["tasks_active"] == 7  # open + in_progress + reopened + blocked


def test_builtin_vars_stories(tmp_path):
    _copy_fixtures_to(tmp_path)
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))

    assert vars["stories_total"] == 5
    assert vars["stories_done"] == 2


def test_builtin_vars_intake(tmp_path):
    _copy_fixtures_to(tmp_path)
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))

    assert vars["intake_open"] == 4
    assert vars["intake_closed"] == 2
    assert vars["intake_total"] == 6
    assert vars["intake_bugs_open"] == 2
    assert vars["intake_features_open"] == 1
    assert vars["intake_gaps_open"] == 1


def test_builtin_vars_convergence(tmp_path):
    _copy_fixtures_to(tmp_path)
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))

    # convergence = stories_done / stories_total * 100 = 2/5*100 = 40.0
    assert vars["convergence"] == 40.0


def test_builtin_vars_missing_files(tmp_path):
    """Missing files produce 0 values, no crash."""
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    assert vars["tasks_open"] == 0
    assert vars["stories_total"] == 0
    assert vars["intake_total"] == 0
    assert vars["convergence"] == 0


# --- helpers ---

def _copy_fixtures_to(dest: Path) -> None:
    """Copy fixture markdown files to dest directory."""
    import shutil
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, dest / f.name)
