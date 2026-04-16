"""Tests for DevLead governance enforcement."""
from pathlib import Path

from devlead.governance import (
    check_active_task,
    scratchpad_add,
    scratchpad_list,
    scratchpad_clear,
    scratchpad_path,
)


def _write_tasks(docs_dir: Path, rows: str) -> None:
    """Write a tasks file with given rows."""
    (docs_dir / "_project_tasks.md").write_text(
        "# Project Tasks\n\n"
        "> Type: PROJECT\n"
        "> Last updated: 2026-04-05 | Open: 0 | In Progress: 0 | Done: 0\n\n"
        "## Active\n\n"
        "| ID | Task | Story | Priority | Status | Assignee | Blockers |\n"
        "|----|----- |-------|----------|--------|----------|----------|\n"
        f"{rows}\n",
        encoding="utf-8",
    )


# --- check_active_task ---


def test_no_tasks_file(tmp_path):
    result = check_active_task(tmp_path)
    assert result["has_active"] is False
    assert result["active_tasks"] == []


def test_no_active_tasks(tmp_path):
    _write_tasks(tmp_path, "| TASK-001 | Do stuff | S-001 | P1 | DONE | claude | — |")
    result = check_active_task(tmp_path)
    assert result["has_active"] is False


def test_has_active_task(tmp_path):
    _write_tasks(
        tmp_path,
        "| TASK-001 | Done task | S-001 | P1 | DONE | claude | — |\n"
        "| TASK-002 | Active task | S-002 | P1 | IN_PROGRESS | claude | — |",
    )
    result = check_active_task(tmp_path)
    assert result["has_active"] is True
    assert "TASK-002" in result["active_tasks"]


def test_multiple_active_tasks(tmp_path):
    _write_tasks(
        tmp_path,
        "| TASK-001 | Task A | S-001 | P1 | IN_PROGRESS | claude | — |\n"
        "| TASK-002 | Task B | S-002 | P1 | IN_PROGRESS | claude | — |",
    )
    result = check_active_task(tmp_path)
    assert result["has_active"] is True
    assert len(result["active_tasks"]) == 2


# --- scratchpad ---


def test_scratchpad_add(tmp_path):
    sid = scratchpad_add(tmp_path, "Some idea", source="user")
    assert sid == "SCRATCH-001"
    assert scratchpad_path(tmp_path).exists()


def test_scratchpad_list(tmp_path):
    scratchpad_add(tmp_path, "Idea one")
    scratchpad_add(tmp_path, "Idea two")
    items = scratchpad_list(tmp_path)
    assert len(items) == 2
    assert items[0]["Key"] == "SCRATCH-001"
    assert items[1]["Key"] == "SCRATCH-002"


def test_scratchpad_list_empty(tmp_path):
    items = scratchpad_list(tmp_path)
    assert items == []


def test_scratchpad_clear(tmp_path):
    scratchpad_add(tmp_path, "Temp idea")
    scratchpad_add(tmp_path, "Another temp")
    count = scratchpad_clear(tmp_path)
    assert count == 2
    items = scratchpad_list(tmp_path)
    assert len(items) == 0


def test_scratchpad_sequential_ids(tmp_path):
    scratchpad_add(tmp_path, "First")
    scratchpad_add(tmp_path, "Second")
    scratchpad_add(tmp_path, "Third")
    items = scratchpad_list(tmp_path)
    assert items[0]["Key"] == "SCRATCH-001"
    assert items[2]["Key"] == "SCRATCH-003"
