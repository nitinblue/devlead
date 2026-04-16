"""Tests for size-based rollover trigger."""

import shutil
from pathlib import Path
from datetime import date

import pytest

from devlead.rollover import should_rollover, do_rollover


FIXTURES = Path(__file__).parent / "fixtures"


def _setup_docs(tmp_path: Path) -> Path:
    docs = tmp_path / "devlead_docs"
    docs.mkdir(exist_ok=True)
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)
    return docs


def test_should_rollover_date_trigger():
    """Date trigger fires on day_of_month."""
    assert should_rollover("date", day_of_month=5, today=date(2026, 4, 5)) is True
    assert should_rollover("date", day_of_month=1, today=date(2026, 4, 5)) is False


def test_should_rollover_size_trigger(tmp_path):
    """Size trigger fires when file exceeds max_lines."""
    docs = _setup_docs(tmp_path)
    tasks_file = docs / "_project_tasks.md"
    # Fixture has ~15 lines, test with low threshold
    assert should_rollover("size", max_lines=10, file_path=tasks_file) is True
    assert should_rollover("size", max_lines=100, file_path=tasks_file) is False


def test_should_rollover_size_missing_file(tmp_path):
    """Size trigger returns False for missing file."""
    assert should_rollover("size", max_lines=10, file_path=tmp_path / "nope.md") is False


def test_rollover_respects_size_trigger(tmp_path):
    """do_rollover with trigger='size' only rolls files exceeding max_lines."""
    docs = _setup_docs(tmp_path)

    # _project_tasks.md has ~15 lines, set threshold at 10
    do_rollover(
        docs,
        ["_project_tasks.md"],
        today=date(2026, 4, 5),
        trigger="size",
        max_lines=10,
    )
    assert (docs / "archive" / "_project_tasks_2026-04.md").exists()


def test_rollover_skips_small_files(tmp_path):
    """do_rollover with trigger='size' skips files under threshold."""
    docs = _setup_docs(tmp_path)

    do_rollover(
        docs,
        ["_project_tasks.md"],
        today=date(2026, 4, 5),
        trigger="size",
        max_lines=1000,
    )
    assert not (docs / "archive" / "_project_tasks_2026-04.md").exists()
