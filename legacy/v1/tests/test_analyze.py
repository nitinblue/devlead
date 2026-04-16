"""Tests for analyze.py — smart TBO-driven project analysis.

Tests use inline markdown tables to verify convergence calculations,
distribution section parsing, shadow work detection, and empty-project safety.
"""

from pathlib import Path

from devlead.analyze import (
    generate_analysis,
    _assess_tbo,
    _detect_shadow_work,
    _section_tables,
)
from devlead.doc_parser import parse_table


# --- Helpers ---

def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _setup_docs(docs: Path, tbos: str = "", stories: str = "",
                tasks: str = "", dist: str = "", scratch: str = "") -> None:
    """Write provided content into the appropriate files."""
    if tbos:
        _write(docs / "_living_business_objectives.md", tbos)
    if stories:
        _write(docs / "_project_stories.md", stories)
    if tasks:
        _write(docs / "_project_tasks.md", tasks)
    if dist:
        _write(docs / "_living_distribution.md", dist)
    if scratch:
        _write(docs / "_scratchpad.md", scratch)


# --- Tests ---

def test_analyze_empty_project(tmp_path):
    """Empty docs dir should not crash; should produce output."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    result = generate_analysis(docs)

    assert isinstance(result, str)
    assert "Project Analysis" in result
    assert "Convergence" in result
    # 0/0 TBOs
    assert "0/0" in result


def test_analyze_convergence(tmp_path):
    """Verify convergence is calculated as done TBOs / total TBOs."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    _setup_docs(docs,
        tbos=(
            "# TBOs\n\n"
            "| ID | Objective | Status | Linked Stories |\n"
            "|-----|-----------|--------|----------------|\n"
            "| TBO-001 | Ship MVP | DONE | S-001 |\n"
            "| TBO-002 | Scale Up | OPEN | S-002 |\n"
            "| TBO-003 | Monetize | OPEN | |\n"
        ),
        stories=(
            "# Stories\n\n"
            "| ID | Story | Status | TBO Link | Epic |\n"
            "|----|-------|--------|----------|------|\n"
            "| S-001 | Login | DONE | TBO-001 | E-001 |\n"
            "| S-002 | Dashboard | OPEN | TBO-002 | E-001 |\n"
        ),
        tasks=(
            "# Tasks\n\n"
            "| ID | Task | Status | Story |\n"
            "|----|------|--------|-------|\n"
            "| T-001 | Build login | DONE | S-001 |\n"
        ),
    )

    result = generate_analysis(docs)

    # 1 of 3 TBOs done = 33%
    assert "1/3" in result
    assert "33%" in result


def test_analyze_distribution(tmp_path):
    """Verify distribution section tables are parsed correctly."""
    dist_text = (
        "# Distribution\n\n"
        "## Open Source Compliance\n\n"
        "| Task | Status |\n"
        "|------|--------|\n"
        "| LICENSE file | DONE |\n"
        "| Header check | OPEN |\n\n"
        "## Package Build and Upload\n\n"
        "| Task | Status |\n"
        "|------|--------|\n"
        "| Build wheel | DONE |\n"
        "| Upload PyPI | DONE |\n"
    )

    sections = _section_tables(dist_text)

    assert "Open Source Compliance" in sections
    assert len(sections["Open Source Compliance"]) == 2
    assert "Package Build and Upload" in sections
    assert len(sections["Package Build and Upload"]) == 2

    # Verify status values
    compliance = sections["Open Source Compliance"]
    done_count = sum(1 for r in compliance if r.get("Status", "").strip() == "DONE")
    assert done_count == 1

    package = sections["Package Build and Upload"]
    done_count = sum(1 for r in package if r.get("Status", "").strip() == "DONE")
    assert done_count == 2


def test_analyze_shadow_work(tmp_path):
    """Tasks with no story link should be flagged as shadow work."""
    task_rows = [
        {"ID": "T-001", "Task": "Linked task", "Status": "OPEN", "Story": "S-001"},
        {"ID": "T-002", "Task": "Orphan task", "Status": "OPEN", "Story": ""},
        {"ID": "T-003", "Task": "Done orphan", "Status": "DONE", "Story": ""},
    ]

    shadow = _detect_shadow_work(task_rows)

    # T-002 is shadow (no story, not done). T-003 is done so excluded.
    assert len(shadow) == 1
    assert shadow[0]["ID"] == "T-002"


def test_assess_tbo_not_started():
    """TBO with no linked stories should say NOT STARTED."""
    tbo = {"ID": "TBO-001", "Objective": "Ship MVP", "Status": "OPEN", "Linked Stories": ""}
    story_map = {}
    task_rows = []

    result = _assess_tbo(tbo, story_map, task_rows)

    assert result["assessment"] == "NOT STARTED -- needs story breakdown"
    assert "No stories linked" in result["blockers"]


def test_assess_tbo_complete():
    """TBO with DONE status should say COMPLETE."""
    tbo = {"ID": "TBO-001", "Objective": "Done thing", "Status": "DONE", "Linked Stories": "S-001"}
    story_map = {"S-001": "DONE"}
    task_rows = []

    result = _assess_tbo(tbo, story_map, task_rows)

    assert result["assessment"] == "COMPLETE"
