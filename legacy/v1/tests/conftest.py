"""Shared test fixtures for DevLead."""

import pytest
from pathlib import Path

# Minimal tasks file with an active task — satisfies the governance gate
_TASKS_WITH_ACTIVE = (
    "# Project Tasks\n\n"
    "> Type: PROJECT\n"
    "> Last updated: 2026-04-05 | Open: 0 | In Progress: 1 | Done: 0\n\n"
    "## Active\n\n"
    "| ID | Task | Story | Priority | Status | Assignee | Blockers |\n"
    "|----|----- |-------|----------|--------|----------|----------|\n"
    "| TASK-001 | Test task | S-001 | P1 | IN_PROGRESS | claude | — |\n"
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with devlead_docs/ subdir."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    # Include a tasks file so governance gate doesn't block
    (docs / "_project_tasks.md").write_text(_TASKS_WITH_ACTIVE, encoding="utf-8")
    return tmp_path


@pytest.fixture
def tmp_docs(tmp_project: Path) -> Path:
    """Return the devlead_docs/ directory inside tmp_project."""
    return tmp_project / "devlead_docs"


@pytest.fixture
def state_file(tmp_docs: Path) -> Path:
    """Return the session_state.json path inside devlead_docs/."""
    return tmp_docs / "session_state.json"
