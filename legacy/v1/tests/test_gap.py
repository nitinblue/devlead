"""Tests for DevLead gap analysis."""
from pathlib import Path

from devlead.gap import run_gap_analysis, format_gaps, EXPECTED_FILES


def _make_docs(tmp_path: Path) -> Path:
    """Create a minimal devlead_docs with all expected files."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    for fname in EXPECTED_FILES:
        (docs / fname).write_text(f"# {fname}\n", encoding="utf-8")
    return docs


def _write_tasks(docs: Path, rows: str) -> None:
    (docs / "_project_tasks.md").write_text(
        "# Project Tasks\n\n"
        "> Type: PROJECT\n"
        "> Last updated: 2026-04-05 | Open: 1 | Done: 0\n\n"
        "| ID | Task | Story | Priority | Status | Assignee | Blockers |\n"
        "|----|----- |-------|----------|--------|----------|----------|\n"
        f"{rows}\n",
        encoding="utf-8",
    )


def _write_stories(docs: Path, rows: str) -> None:
    (docs / "_project_stories.md").write_text(
        "# Project Stories\n\n"
        "> Type: PROJECT\n\n"
        "| ID | Story | Epic | Status |\n"
        "|----|-------|------|--------|\n"
        f"{rows}\n",
        encoding="utf-8",
    )


# --- No docs dir ---


def test_no_docs_dir(tmp_path):
    gaps = run_gap_analysis(tmp_path)
    assert len(gaps) == 1
    assert gaps[0]["category"] == "MISSING_FILE"
    assert gaps[0]["severity"] == "P1"


# --- Missing files ---


def test_missing_files_detected(tmp_path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    # Create only one file
    (docs / "_project_status.md").write_text("# Status\n", encoding="utf-8")

    gaps = run_gap_analysis(tmp_path)
    missing = [g for g in gaps if g["category"] == "MISSING_FILE"]
    # Should detect all missing expected files except _project_status.md
    expected_missing = [f for f in EXPECTED_FILES if f != "_project_status.md"]
    assert len(missing) == len(expected_missing)


def test_no_missing_files(tmp_path):
    _make_docs(tmp_path)
    gaps = run_gap_analysis(tmp_path)
    missing = [g for g in gaps if g["category"] == "MISSING_FILE"]
    assert len(missing) == 0


# --- Shadow work ---


def test_shadow_work_detected(tmp_path):
    docs = _make_docs(tmp_path)
    _write_tasks(docs,
        "| TASK-001 | Do stuff | \u2014 | P1 | OPEN | claude | \u2014 |\n"
        "| TASK-002 | More stuff |  | P2 | IN_PROGRESS | claude | \u2014 |")

    gaps = run_gap_analysis(tmp_path)
    shadow = [g for g in gaps if g["category"] == "SHADOW_WORK"]
    assert len(shadow) == 2
    assert shadow[0]["severity"] == "P1"
    assert "TASK-001" in shadow[0]["message"]
    assert "TASK-002" in shadow[1]["message"]


def test_shadow_work_skips_done(tmp_path):
    docs = _make_docs(tmp_path)
    _write_tasks(docs,
        "| TASK-001 | Old task | \u2014 | P1 | DONE | claude | \u2014 |")

    gaps = run_gap_analysis(tmp_path)
    shadow = [g for g in gaps if g["category"] == "SHADOW_WORK"]
    assert len(shadow) == 0


def test_no_shadow_work_when_linked(tmp_path):
    docs = _make_docs(tmp_path)
    _write_tasks(docs,
        "| TASK-001 | Do stuff | S-001 | P1 | OPEN | claude | \u2014 |")

    gaps = run_gap_analysis(tmp_path)
    shadow = [g for g in gaps if g["category"] == "SHADOW_WORK"]
    assert len(shadow) == 0


# --- Orphan stories ---


def test_orphan_story_detected(tmp_path):
    docs = _make_docs(tmp_path)
    _write_stories(docs,
        "| S-001 | A story | \u2014 | OPEN |\n"
        "| S-002 | Linked | E-001 | OPEN |")

    gaps = run_gap_analysis(tmp_path)
    orphans = [g for g in gaps if g["category"] == "ORPHAN_STORY"]
    assert len(orphans) == 1
    assert "S-001" in orphans[0]["message"]


def test_orphan_story_skips_done(tmp_path):
    docs = _make_docs(tmp_path)
    _write_stories(docs,
        "| S-001 | Old story | \u2014 | DONE |")

    gaps = run_gap_analysis(tmp_path)
    orphans = [g for g in gaps if g["category"] == "ORPHAN_STORY"]
    assert len(orphans) == 0


def test_no_orphan_when_stories_missing(tmp_path):
    docs = _make_docs(tmp_path)
    # Remove stories file
    (docs / "_project_stories.md").unlink()

    gaps = run_gap_analysis(tmp_path)
    orphans = [g for g in gaps if g["category"] == "ORPHAN_STORY"]
    assert len(orphans) == 0


# --- Intake mismatches ---


def test_intake_mismatch_detected(tmp_path):
    docs = _make_docs(tmp_path)
    (docs / "_intake_features.md").write_text(
        "# Intake Features\n\n"
        "> Type: INTAKE\n"
        "> Last updated: 2026-04-05 | Open: 5 | Closed: 0\n\n"
        "| ID | Feature | Status |\n"
        "|----|---------|--------|\n"
        "| F-001 | Feature A | OPEN |\n"
        "| F-002 | Feature B | OPEN |\n",
        encoding="utf-8",
    )

    gaps = run_gap_analysis(tmp_path)
    mismatches = [g for g in gaps if g["category"] == "INTAKE_MISMATCH"]
    assert len(mismatches) >= 1
    assert "open=5" in mismatches[0]["message"]
    assert "actual rows=2" in mismatches[0]["message"]


def test_intake_no_mismatch_when_correct(tmp_path):
    docs = _make_docs(tmp_path)
    (docs / "_intake_features.md").write_text(
        "# Intake Features\n\n"
        "> Type: INTAKE\n"
        "> Last updated: 2026-04-05 | Open: 2 | Closed: 1\n\n"
        "| ID | Feature | Status |\n"
        "|----|---------|--------|\n"
        "| F-001 | Feature A | OPEN |\n"
        "| F-002 | Feature B | OPEN |\n"
        "| F-003 | Feature C | CLOSED |\n",
        encoding="utf-8",
    )

    gaps = run_gap_analysis(tmp_path)
    mismatches = [g for g in gaps if g["category"] == "INTAKE_MISMATCH"]
    assert len(mismatches) == 0


# --- File size violations ---


def test_file_size_violation(tmp_path):
    docs = _make_docs(tmp_path)
    src = tmp_path / "src" / "devlead"
    src.mkdir(parents=True)
    # Write a file over 200 lines
    (src / "big_module.py").write_text(
        "\n".join([f"# line {i}" for i in range(250)]),
        encoding="utf-8",
    )
    # Write a file under 200 lines
    (src / "small_module.py").write_text(
        "\n".join([f"# line {i}" for i in range(50)]),
        encoding="utf-8",
    )

    gaps = run_gap_analysis(tmp_path)
    size_gaps = [g for g in gaps if g["category"] == "FILE_SIZE"]
    assert len(size_gaps) == 1
    assert "big_module.py" in size_gaps[0]["message"]
    assert "250" in size_gaps[0]["message"]


def test_no_file_size_gap_when_no_src(tmp_path):
    docs = _make_docs(tmp_path)
    gaps = run_gap_analysis(tmp_path)
    size_gaps = [g for g in gaps if g["category"] == "FILE_SIZE"]
    assert len(size_gaps) == 0


# --- Auto-incrementing IDs ---


def test_gap_ids_sequential(tmp_path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    # Will produce multiple MISSING_FILE gaps
    gaps = run_gap_analysis(tmp_path)
    for i, g in enumerate(gaps):
        assert g["id"] == f"GAP-{i + 1:03d}"


# --- format_gaps ---


def test_format_gaps_no_gaps(tmp_path):
    output = format_gaps([])
    assert "No governance gaps" in output


def test_format_gaps_with_gaps(tmp_path):
    gaps = [
        {"id": "GAP-001", "category": "SHADOW_WORK",
         "severity": "P1", "message": "Task X has no Story"},
        {"id": "GAP-002", "category": "FILE_SIZE",
         "severity": "P2", "message": "big.py: 300 lines"},
    ]
    output = format_gaps(gaps)
    assert "P1" in output
    assert "P2" in output
    assert "GAP-001" in output
    assert "GAP-002" in output
    assert "Total gaps" in output
