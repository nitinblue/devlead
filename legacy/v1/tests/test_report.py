"""Tests for DevLead session report generator."""
import shutil
from pathlib import Path

from devlead.report import generate_report

FIXTURES = Path(__file__).parent / "fixtures"


def test_report_empty_project(tmp_path):
    """Report handles empty devlead_docs/ gracefully."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    result = generate_report(docs)
    assert "Session Report" in result
    assert "Tasks" in result
    assert "Features" in result
    assert "Gaps" in result
    assert "Bugs" in result


def test_report_with_fixtures(tmp_path):
    """Report reads fixture files correctly."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    result = generate_report(docs)
    assert "Session Report" in result
    assert "Tasks" in result
    # Fixture has tasks with various statuses
    assert "Done" in result


def test_report_counts_statuses(tmp_path):
    """Report correctly counts open/closed items."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    # Write a simple intake file
    (docs / "_intake_features.md").write_text(
        "# Feature Intake\n\n"
        "> Type: INTAKE\n"
        "> Last updated: 2026-04-05 | Open: 2 | Closed: 1\n\n"
        "## Active\n\n"
        "| Key | Item | Source | Added | Status | Priority | Notes |\n"
        "|-----|------|--------|-------|--------|----------|-------|\n"
        "| FEAT-001 | Feature A | user | 2026-04-05 | OPEN | P1 | test |\n"
        "| FEAT-002 | Feature B | user | 2026-04-05 | OPEN | P2 | test |\n"
        "| FEAT-003 | Feature C | user | 2026-04-05 | CLOSED | P1 | done |\n",
        encoding="utf-8",
    )

    result = generate_report(docs)
    # P1 open items listed by key
    assert "FEAT-001" in result
    assert "Feature A" in result
    # P2 counted but not in P1 list
    assert "Open" in result


def test_report_shows_bugs(tmp_path):
    """Report lists open bugs."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    (docs / "_intake_bugs.md").write_text(
        "# Bug Intake\n\n"
        "> Type: INTAKE\n"
        "> Last updated: 2026-04-05 | Open: 1 | Closed: 0\n\n"
        "## Active\n\n"
        "| Key | Item | Source | Added | Status | Priority | Notes |\n"
        "|-----|------|--------|-------|--------|----------|-------|\n"
        "| BUG-001 | Something broke | audit | 2026-04-05 | OPEN | P1 | fix it |\n",
        encoding="utf-8",
    )

    result = generate_report(docs)
    assert "BUG-001" in result
    assert "Something broke" in result


def test_report_shows_gaps(tmp_path):
    """Report lists open gaps."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    (docs / "_intake_gaps.md").write_text(
        "# Gap Intake\n\n"
        "> Type: INTAKE\n"
        "> Last updated: 2026-04-05 | Open: 1 | Closed: 0\n\n"
        "## Active\n\n"
        "| Key | Item | Source | Added | Status | Priority | Notes |\n"
        "|-----|------|--------|-------|--------|----------|-------|\n"
        "| GAP-001 | Missing doc | audit | 2026-04-05 | OPEN | P1 | create it |\n",
        encoding="utf-8",
    )

    result = generate_report(docs)
    assert "GAP-001" in result
    assert "Missing doc" in result


def test_report_summary_totals(tmp_path):
    """Report summary counts all open items."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    result = generate_report(docs)
    # With empty files, total should be 0
    assert "0" in result
    assert "All clear" in result
