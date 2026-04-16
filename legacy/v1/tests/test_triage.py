"""Tests for triage.py — scratchpad item classification and intake routing.

Tests use inline markdown files (no fixtures) to verify pending item detection,
key sequencing, intake routing, and scratchpad archival.
"""

from pathlib import Path

from devlead.triage import (
    get_pending_items,
    get_next_key,
    triage_item,
    INTAKE_MAP,
)


# --- Helpers ---

def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


SCRATCHPAD_WITH_ITEMS = """\
# Scratchpad

| Key | Item | Source | Added | Status |
|-----|------|--------|-------|--------|
| SCRATCH-001 | Add dark mode | user | 2026-04-01 | PENDING |
| SCRATCH-002 | Fix login crash | user | 2026-04-02 | PENDING |
| SCRATCH-003 | Old idea | user | 2026-03-01 | TRIAGED |

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|
"""

FEATURES_WITH_EXISTING = """\
# Feature Intake

> Type: INTAKE
> Last updated: 2026-04-05 | Open: 2 | Closed: 0

## Active

| Key | Item | Source | Added | Status | Priority | Notes |
|-----|------|--------|-------|--------|----------|-------|
| FEAT-001 | Existing feature 1 | user | 2026-04-01 | OPEN | P2 | |
| FEAT-002 | Existing feature 2 | user | 2026-04-02 | OPEN | P1 | |

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|
"""

BUGS_EMPTY = """\
# Bug Intake

> Type: INTAKE
> Last updated: 2026-04-05 | Open: 0 | Closed: 0

## Active

| Key | Item | Source | Added | Status | Priority | Notes |
|-----|------|--------|-------|--------|----------|-------|

## Archive

| Key | Item | Resolved | Resolution |
|-----|------|----------|------------|
"""


# --- Tests ---

def test_get_pending_items(tmp_path):
    """Items with PENDING status should be returned."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_scratchpad.md", SCRATCHPAD_WITH_ITEMS)

    pending = get_pending_items(docs)

    assert len(pending) == 2
    keys = [p["Key"] for p in pending]
    assert "SCRATCH-001" in keys
    assert "SCRATCH-002" in keys
    # TRIAGED item should not appear
    assert all(p["Status"].strip().upper() == "PENDING" for p in pending)


def test_get_pending_items_no_scratchpad(tmp_path):
    """Missing scratchpad file should return empty list."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    pending = get_pending_items(docs)
    assert pending == []


def test_get_next_key(tmp_path):
    """Next key should follow the highest existing key number."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_intake_features.md", FEATURES_WITH_EXISTING)

    key = get_next_key(docs, "feature")

    assert key == "FEAT-003"


def test_get_next_key_empty_file(tmp_path):
    """Empty intake file should start at 001."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_intake_bugs.md", BUGS_EMPTY)

    key = get_next_key(docs, "bug")

    assert key == "BUG-001"


def test_get_next_key_no_file(tmp_path):
    """Missing intake file should start at 001."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    key = get_next_key(docs, "gap")

    assert key == "GAP-001"


def test_triage_item(tmp_path):
    """Triaging to features should append a row to the intake file."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_scratchpad.md", SCRATCHPAD_WITH_ITEMS)
    _write(docs / "_intake_features.md", FEATURES_WITH_EXISTING)

    new_key = triage_item(docs, "SCRATCH-001", "feature", "P2", "Add dark mode")

    assert new_key == "FEAT-003"

    # Verify intake file has the new row
    intake_text = (docs / "_intake_features.md").read_text(encoding="utf-8")
    assert "FEAT-003" in intake_text
    assert "Add dark mode" in intake_text
    assert "P2" in intake_text


def test_triage_to_bugs(tmp_path):
    """Triaging to bugs should create a BUG-001 entry."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_scratchpad.md", SCRATCHPAD_WITH_ITEMS)
    _write(docs / "_intake_bugs.md", BUGS_EMPTY)

    new_key = triage_item(docs, "SCRATCH-002", "bug", "P1", "Fix login crash")

    assert new_key == "BUG-001"

    intake_text = (docs / "_intake_bugs.md").read_text(encoding="utf-8")
    assert "BUG-001" in intake_text
    assert "Fix login crash" in intake_text


def test_triage_marks_as_triaged(tmp_path):
    """After triage, the scratchpad item should be removed from active rows."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_scratchpad.md", SCRATCHPAD_WITH_ITEMS)
    _write(docs / "_intake_features.md", FEATURES_WITH_EXISTING)

    triage_item(docs, "SCRATCH-001", "feature", "P2", "Add dark mode")

    sp_text = (docs / "_scratchpad.md").read_text(encoding="utf-8")

    # SCRATCH-001 should no longer be in the active table as PENDING
    # It should appear in the Archive section as TRIAGED
    active_lines = []
    in_archive = False
    for line in sp_text.splitlines():
        if "## Archive" in line:
            in_archive = True
        if not in_archive and "SCRATCH-001" in line:
            active_lines.append(line)

    # Should not appear in active section anymore
    assert len(active_lines) == 0

    # Should appear in archive
    assert "SCRATCH-001" in sp_text
    assert "TRIAGED" in sp_text
