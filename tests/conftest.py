"""Shared test fixtures for DevLead."""

import pytest
from pathlib import Path


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with claude_docs/ subdir."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    return tmp_path


@pytest.fixture
def tmp_docs(tmp_project: Path) -> Path:
    """Return the claude_docs/ directory inside tmp_project."""
    return tmp_project / "claude_docs"


@pytest.fixture
def state_file(tmp_docs: Path) -> Path:
    """Return the session_state.json path inside claude_docs/."""
    return tmp_docs / "session_state.json"
