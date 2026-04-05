"""Tests for rollover.py — monthly archival with open item carry-forward."""

import shutil
from pathlib import Path
from datetime import date

import pytest

from devlead.rollover import do_rollover


FIXTURES = Path(__file__).parent / "fixtures"


def _setup_docs(tmp_path: Path) -> Path:
    """Copy fixture docs to tmp_path/claude_docs."""
    docs = tmp_path / "claude_docs"
    docs.mkdir(exist_ok=True)
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)
    return docs


def test_rollover_creates_archive_dir(tmp_path):
    """Rollover creates claude_docs/archive/."""
    docs = _setup_docs(tmp_path)
    files = ["_project_tasks.md", "_intake_bugs.md"]
    do_rollover(docs, files, today=date(2026, 4, 5))
    assert (docs / "archive").is_dir()


def test_rollover_creates_archive_files(tmp_path):
    """Rollover copies files to archive with month suffix."""
    docs = _setup_docs(tmp_path)
    files = ["_project_tasks.md", "_intake_bugs.md"]
    do_rollover(docs, files, today=date(2026, 4, 5))
    assert (docs / "archive" / "_project_tasks_2026-04.md").exists()
    assert (docs / "archive" / "_intake_bugs_2026-04.md").exists()


def test_rollover_archive_is_full_copy(tmp_path):
    """Archive file contains the complete original content."""
    docs = _setup_docs(tmp_path)
    original = (docs / "_project_tasks.md").read_text()
    do_rollover(docs, ["_project_tasks.md"], today=date(2026, 4, 5))
    archive = (docs / "archive" / "_project_tasks_2026-04.md").read_text()
    assert archive == original


def test_rollover_carries_forward_open(tmp_path):
    """Current file retains only open/active items after rollover."""
    docs = _setup_docs(tmp_path)
    do_rollover(docs, ["_intake_bugs.md"], today=date(2026, 4, 5))
    current = (docs / "_intake_bugs.md").read_text()
    # OPEN items remain
    assert "BUG-001" in current
    assert "BUG-002" in current
    # CLOSED items removed
    assert "BUG-003" not in current


def test_rollover_preserves_header(tmp_path):
    """Current file keeps its header/table structure after rollover."""
    docs = _setup_docs(tmp_path)
    do_rollover(docs, ["_intake_bugs.md"], today=date(2026, 4, 5))
    current = (docs / "_intake_bugs.md").read_text()
    assert "# Bug Intake" in current
    assert "| Key |" in current


def test_rollover_idempotent_same_month(tmp_path):
    """Running rollover twice in same month doesn't duplicate."""
    docs = _setup_docs(tmp_path)
    files = ["_intake_bugs.md"]
    do_rollover(docs, files, today=date(2026, 4, 5))
    first_archive = (docs / "archive" / "_intake_bugs_2026-04.md").read_text()
    do_rollover(docs, files, today=date(2026, 4, 5))
    second_archive = (docs / "archive" / "_intake_bugs_2026-04.md").read_text()
    # Archive should not change on second run
    assert first_archive == second_archive


def test_rollover_missing_file_skipped(tmp_path):
    """Rollover skips files that don't exist."""
    docs = _setup_docs(tmp_path)
    # Should not raise
    do_rollover(docs, ["_nonexistent.md"], today=date(2026, 4, 5))


def test_rollover_tasks_carry_forward(tmp_path):
    """Task rollover: DONE removed, OPEN/IN_PROGRESS/BLOCKED kept."""
    docs = _setup_docs(tmp_path)
    do_rollover(docs, ["_project_tasks.md"], today=date(2026, 4, 5))
    current = (docs / "_project_tasks.md").read_text()
    # DONE tasks should be removed
    assert "TASK-001" not in current  # DONE
    assert "TASK-002" not in current  # DONE
    assert "TASK-010" not in current  # DONE
    # Open/active tasks remain
    assert "TASK-003" in current  # IN_PROGRESS
    assert "TASK-004" in current  # OPEN
    assert "TASK-008" in current  # BLOCKED
