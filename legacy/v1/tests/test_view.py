"""Tests for view.py — TBO -> Story -> Task hierarchy display.

Tests use inline markdown tables (no fixtures) to verify the hierarchy
rendering, shadow work detection, and empty-project resilience.
"""

from pathlib import Path

from devlead.view import generate_project_view


# --- Helpers ---

def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _make_tbo_file(docs: Path, rows: list[tuple[str, str, str, str]]) -> None:
    """Write a _living_business_objectives.md with given (ID, Objective, Status, Linked Stories)."""
    lines = [
        "# Business Objectives\n",
        "| ID | Objective | Status | Linked Stories |",
        "|-----|-----------|--------|----------------|",
    ]
    for rid, obj, status, linked in rows:
        lines.append(f"| {rid} | {obj} | {status} | {linked} |")
    _write(docs / "_living_business_objectives.md", "\n".join(lines))


def _make_story_file(docs: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    """Write _project_stories.md with (ID, Story, Status, TBO Link, Epic)."""
    lines = [
        "# Stories\n",
        "| ID | Story | Status | TBO Link | Epic |",
        "|----|-------|--------|----------|------|",
    ]
    for sid, story, status, tbo, epic in rows:
        lines.append(f"| {sid} | {story} | {status} | {tbo} | {epic} |")
    _write(docs / "_project_stories.md", "\n".join(lines))


def _make_task_file(docs: Path, rows: list[tuple[str, str, str, str]]) -> None:
    """Write _project_tasks.md with (ID, Task, Status, Story)."""
    lines = [
        "# Tasks\n",
        "| ID | Task | Status | Story |",
        "|----|------|--------|-------|",
    ]
    for tid, task, status, story in rows:
        lines.append(f"| {tid} | {task} | {status} | {story} |")
    _write(docs / "_project_tasks.md", "\n".join(lines))


# --- Tests ---

def test_view_empty_project(tmp_path):
    """Empty devlead_docs directory should not crash."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    result = generate_project_view(docs)

    assert isinstance(result, str)
    # Summary line should show all zeros
    assert "0 TBOs" in result
    assert "0 stories" in result
    assert "0 tasks" in result
    assert "0 shadow" in result


def test_view_with_tbos(tmp_path):
    """Full TBO -> Story -> Task hierarchy should appear in output."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    _make_tbo_file(docs, [
        ("TBO-001", "Ship MVP", "OPEN", "S-001, S-002"),
    ])
    _make_story_file(docs, [
        ("S-001", "User login", "DONE", "TBO-001", "E-001"),
        ("S-002", "Dashboard", "IN_PROGRESS", "TBO-001", "E-001"),
    ])
    _make_task_file(docs, [
        ("T-001", "Build login form", "DONE", "S-001"),
        ("T-002", "Build dashboard page", "IN_PROGRESS", "S-002"),
    ])

    result = generate_project_view(docs)

    # TBO appears
    assert "TBO-001" in result
    assert "Ship MVP" in result

    # Stories appear
    assert "S-001" in result
    assert "User login" in result
    assert "S-002" in result
    assert "Dashboard" in result

    # Tasks appear
    assert "T-001" in result
    assert "T-002" in result

    # Summary line
    assert "1 TBOs" in result
    assert "2 stories" in result
    assert "2 tasks" in result
    assert "0 shadow" in result


def test_view_shadow_work(tmp_path):
    """A task with no story link should show as shadow work."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    _make_tbo_file(docs, [
        ("TBO-001", "Ship MVP", "OPEN", "S-001"),
    ])
    _make_story_file(docs, [
        ("S-001", "User login", "OPEN", "TBO-001", "E-001"),
    ])
    _make_task_file(docs, [
        ("T-001", "Build login form", "OPEN", "S-001"),
        ("T-099", "Random cleanup", "OPEN", ""),
    ])

    result = generate_project_view(docs)

    # Shadow work section should appear
    assert "SHADOW WORK" in result
    assert "T-099" in result
    assert "Random cleanup" in result

    # Summary should show 1 shadow item
    assert "1 shadow" in result
