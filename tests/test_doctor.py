"""Tests for devlead doctor — health check."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from devlead.doctor import do_doctor

FIXTURES = Path(__file__).parent / "fixtures"


def _full_setup(tmp_path: Path) -> Path:
    """Set up a complete DevLead project."""
    from devlead.init import do_init
    do_init(tmp_path)
    return tmp_path


def test_doctor_all_ok(tmp_path):
    """Doctor reports all OK on a fresh init."""
    _full_setup(tmp_path)
    results = do_doctor(tmp_path)
    # All checks should pass
    errors = [r for r in results if r["status"] == "ERROR"]
    assert len(errors) == 0


def test_doctor_missing_docs_dir(tmp_path):
    """Doctor reports missing claude_docs/."""
    results = do_doctor(tmp_path)
    statuses = {r["check"]: r["status"] for r in results}
    assert statuses["claude_docs/ exists"] == "ERROR"


def test_doctor_missing_toml(tmp_path):
    """Doctor reports missing devlead.toml."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    results = do_doctor(tmp_path)
    statuses = {r["check"]: r["status"] for r in results}
    assert statuses["devlead.toml found"] == "WARN"


def test_doctor_missing_hooks(tmp_path):
    """Doctor reports missing hooks config."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    results = do_doctor(tmp_path)
    statuses = {r["check"]: r["status"] for r in results}
    assert statuses[".claude/settings.json has hooks"] == "WARN"


def test_doctor_missing_doc_file(tmp_path):
    """Doctor reports missing doc files."""
    _full_setup(tmp_path)
    # Remove one file
    (tmp_path / "claude_docs" / "_intake_bugs.md").unlink()
    results = do_doctor(tmp_path)
    warns = [r for r in results if r["status"] == "WARN" and "bugs" in r["check"]]
    assert len(warns) >= 1


def test_doctor_gitignore_check(tmp_path):
    """Doctor checks session_state.json is in .gitignore."""
    _full_setup(tmp_path)
    results = do_doctor(tmp_path)
    statuses = {r["check"]: r["status"] for r in results}
    assert statuses["session_state.json is gitignored"] == "OK"


def test_doctor_cli(tmp_path):
    """devlead doctor works from CLI."""
    from devlead.init import do_init
    do_init(tmp_path)
    result = subprocess.run(
        [sys.executable, "-m", "devlead", "doctor"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert "[OK]" in result.stdout
