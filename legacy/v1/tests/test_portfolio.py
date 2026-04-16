"""Tests for portfolio.py — multi-project workspace, cross-project KPIs."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from devlead.portfolio import (
    add_project,
    remove_project,
    list_projects,
    load_workspace,
    save_workspace,
    compute_portfolio_kpis,
    format_portfolio_dashboard,
)


FIXTURES = Path(__file__).parent / "fixtures"


def _setup_project(tmp_path: Path, name: str) -> Path:
    """Create a fake project with devlead_docs."""
    proj = tmp_path / name
    proj.mkdir()
    docs = proj / "devlead_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)
    return proj


def test_add_project(tmp_path):
    """Add a project to workspace."""
    workspace = tmp_path / ".devlead"
    proj = _setup_project(tmp_path, "proj_a")
    add_project(workspace, str(proj), "proj_a")
    ws = load_workspace(workspace)
    assert len(ws["projects"]) == 1
    assert ws["projects"][0]["name"] == "proj_a"


def test_add_duplicate(tmp_path):
    """Adding same project twice doesn't duplicate."""
    workspace = tmp_path / ".devlead"
    proj = _setup_project(tmp_path, "proj_a")
    add_project(workspace, str(proj), "proj_a")
    add_project(workspace, str(proj), "proj_a")
    ws = load_workspace(workspace)
    assert len(ws["projects"]) == 1


def test_remove_project(tmp_path):
    """Remove a project from workspace."""
    workspace = tmp_path / ".devlead"
    proj = _setup_project(tmp_path, "proj_a")
    add_project(workspace, str(proj), "proj_a")
    remove_project(workspace, "proj_a")
    ws = load_workspace(workspace)
    assert len(ws["projects"]) == 0


def test_list_projects(tmp_path):
    """List registered projects."""
    workspace = tmp_path / ".devlead"
    proj_a = _setup_project(tmp_path, "proj_a")
    proj_b = _setup_project(tmp_path, "proj_b")
    add_project(workspace, str(proj_a), "proj_a")
    add_project(workspace, str(proj_b), "proj_b")
    projects = list_projects(workspace)
    assert len(projects) == 2
    names = [p["name"] for p in projects]
    assert "proj_a" in names
    assert "proj_b" in names


def test_compute_portfolio_kpis(tmp_path):
    """Portfolio KPIs compute across projects."""
    workspace = tmp_path / ".devlead"
    proj_a = _setup_project(tmp_path, "proj_a")
    proj_b = _setup_project(tmp_path, "proj_b")
    add_project(workspace, str(proj_a), "proj_a")
    add_project(workspace, str(proj_b), "proj_b")

    results = compute_portfolio_kpis(workspace)
    assert len(results) > 0
    names = [r.name for r in results]
    assert "Portfolio Convergence" in names


def test_format_portfolio_dashboard(tmp_path):
    """Dashboard output includes project table."""
    workspace = tmp_path / ".devlead"
    proj = _setup_project(tmp_path, "proj_a")
    add_project(workspace, str(proj), "proj_a")

    results = compute_portfolio_kpis(workspace)
    output = format_portfolio_dashboard(
        list_projects(workspace), results
    )
    assert "proj_a" in output
    assert "Portfolio" in output


def test_portfolio_cli_list(tmp_path):
    """devlead portfolio list works from CLI."""
    # Need to setup workspace in home dir equivalent
    # This is a simplified test - just verify the command parses
    result = subprocess.run(
        [sys.executable, "-m", "devlead", "portfolio", "list"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    # Should run without crash (may show empty list)
    assert result.returncode == 0
