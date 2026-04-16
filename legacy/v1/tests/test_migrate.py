"""Tests for migrate.py — project bootstrap and migration.

Tests use tmp_path to verify scanning, file creation, preservation of
existing files, and dry-run behavior.
"""

from pathlib import Path

from devlead.migrate import (
    scan_existing,
    do_migrate,
    do_migrate_dry_run,
    EXPECTED_DOC_FILES,
)


# --- Helpers ---

def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- Tests ---

def test_scan_empty_project(tmp_path):
    """Empty project dir should report nothing found, everything missing."""
    result = scan_existing(tmp_path)

    assert result["docs_dir_exists"] is False
    assert result["found_files"] == []
    # All expected files should be missing
    assert len(result["missing_files"]) == len(EXPECTED_DOC_FILES)


def test_scan_existing_project(tmp_path):
    """Project with some files should list them as found."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_project_status.md", "# Status\n")
    _write(docs / "_project_tasks.md", "# Tasks\n")
    _write(tmp_path / "CLAUDE.md", "# CLAUDE\n")
    _write(tmp_path / "devlead.toml", "[project]\n")

    result = scan_existing(tmp_path)

    assert result["docs_dir_exists"] is True
    assert "devlead_docs/_project_status.md" in result["found_files"]
    assert "devlead_docs/_project_tasks.md" in result["found_files"]
    assert "CLAUDE.md" in result["found_files"]
    assert "devlead.toml" in result["found_files"]

    # Those two files exist, so missing should exclude them
    assert "_project_status.md" not in result["missing_files"]
    assert "_project_tasks.md" not in result["missing_files"]

    # But other expected files should still be missing
    assert "_project_roadmap.md" in result["missing_files"]


def test_migrate_creates_missing(tmp_path):
    """Migration should create all expected files when none exist."""
    result = do_migrate(tmp_path)

    assert len(result["created"]) > 0
    assert len(result["skipped"]) == 0

    # devlead_docs/ should exist now
    docs = tmp_path / "devlead_docs"
    assert docs.is_dir()

    # All expected doc files should exist
    for fname in EXPECTED_DOC_FILES:
        assert (docs / fname).exists(), f"{fname} should have been created"

    # devlead.toml should exist
    # (may or may not exist depending on scaffold availability)
    assert "devlead.toml" in result["created"] or "devlead.toml" in result["skipped"]


def test_migrate_preserves_existing(tmp_path):
    """Existing files should not be overwritten."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    # Create a file with custom content
    custom_content = "# My Custom Tasks\n\nDo not overwrite me.\n"
    _write(docs / "_project_tasks.md", custom_content)

    result = do_migrate(tmp_path)

    # The existing file should be in skipped, not created
    assert "devlead_docs/_project_tasks.md" in result["skipped"]
    assert "devlead_docs/_project_tasks.md" not in result["created"]

    # Content should be preserved
    actual = (docs / "_project_tasks.md").read_text()
    assert actual == custom_content


def test_migrate_dry_run(tmp_path):
    """Dry run should report what would happen but create nothing."""
    result = do_migrate_dry_run(tmp_path)

    assert len(result["would_create"]) > 0
    assert "devlead_docs/" in result["would_create"]

    # Nothing should actually exist
    docs = tmp_path / "devlead_docs"
    assert not docs.exists()

    # devlead.toml should not exist
    assert not (tmp_path / "devlead.toml").exists()


def test_migrate_dry_run_with_existing(tmp_path):
    """Dry run should list existing files as already_exists."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _write(docs / "_project_tasks.md", "# Tasks\n")

    result = do_migrate_dry_run(tmp_path)

    assert "devlead_docs/_project_tasks.md" in result["already_exists"]
    assert "devlead_docs/_project_tasks.md" not in result["would_create"]
    # devlead_docs/ already exists, so not in would_create
    assert "devlead_docs/" not in result["would_create"]
