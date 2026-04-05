"""Integration tests for CLI commands with KPIs."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _run(args: list[str], cwd: str | Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "devlead"] + args,
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def test_start_outputs_json(tmp_path):
    """devlead start outputs JSON with systemMessage."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    result = _run(["start"], cwd=tmp_path)
    # start calls sys.exit(0) — returncode 0
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert "systemMessage" in output
    assert "ORIENT" in output["systemMessage"]


def test_start_creates_state_file(tmp_path):
    """devlead start creates session_state.json."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    _run(["start"], cwd=tmp_path)
    assert (docs / "session_state.json").exists()


def test_status_shows_state(tmp_path):
    """devlead status shows current state."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    _run(["start"], cwd=tmp_path)
    result = _run(["status"], cwd=tmp_path)
    assert result.returncode == 0
    assert "ORIENT" in result.stdout
    assert "Pipeline:" in result.stdout


def test_status_no_session(tmp_path):
    """devlead status without start shows error."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    result = _run(["status"], cwd=tmp_path)
    assert result.returncode == 1
    assert "No active session" in result.stderr


def test_kpis_shows_dashboard(tmp_path):
    """devlead kpis shows full dashboard."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    result = _run(["kpis"], cwd=tmp_path)
    assert result.returncode == 0
    assert "LLM EFFECTIVENESS" in result.stdout
    assert "DELIVERY" in result.stdout
    assert "PROJECT HEALTH" in result.stdout


def test_gate_blocks_in_orient(tmp_path):
    """devlead gate EXECUTE blocks in ORIENT state."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    _run(["start"], cwd=tmp_path)

    result = _run(["gate", "EXECUTE"], cwd=tmp_path)
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_gate_allows_in_execute(tmp_path):
    """devlead gate EXECUTE allows after transitioning to EXECUTE."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    _run(["start"], cwd=tmp_path)

    # Complete ORIENT checklist
    for key in ["status_read", "tasks_read", "intake_scanned", "kpis_reported"]:
        _run(["checklist", "ORIENT", key], cwd=tmp_path)
    # Transition to INTAKE
    _run(["transition", "INTAKE"], cwd=tmp_path)
    # Complete INTAKE checklist
    for key in ["requests_captured", "triaged"]:
        _run(["checklist", "INTAKE", key], cwd=tmp_path)
    # Transition to PLAN
    _run(["transition", "PLAN"], cwd=tmp_path)
    # Transition to EXECUTE
    _run(["transition", "EXECUTE"], cwd=tmp_path)

    result = _run(["gate", "EXECUTE"], cwd=tmp_path)
    assert result.returncode == 0


def test_full_lifecycle(tmp_path):
    """Full state lifecycle: ORIENT → INTAKE → PLAN → EXECUTE → UPDATE → SESSION_END."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()

    # Start
    r = _run(["start"], cwd=tmp_path)
    assert r.returncode == 0

    # ORIENT → INTAKE
    for key in ["status_read", "tasks_read", "intake_scanned", "kpis_reported"]:
        _run(["checklist", "ORIENT", key], cwd=tmp_path)
    r = _run(["transition", "INTAKE"], cwd=tmp_path)
    assert r.returncode == 0

    # INTAKE → PLAN
    for key in ["requests_captured", "triaged"]:
        _run(["checklist", "INTAKE", key], cwd=tmp_path)
    r = _run(["transition", "PLAN"], cwd=tmp_path)
    assert r.returncode == 0

    # PLAN → EXECUTE
    r = _run(["transition", "EXECUTE"], cwd=tmp_path)
    assert r.returncode == 0

    # EXECUTE → UPDATE
    r = _run(["transition", "UPDATE"], cwd=tmp_path)
    assert r.returncode == 0

    # UPDATE → SESSION_END
    for key in ["intake_updated", "tasks_updated", "status_updated", "living_reviewed", "memory_derived"]:
        _run(["checklist", "UPDATE", key], cwd=tmp_path)
    r = _run(["transition", "SESSION_END"], cwd=tmp_path)
    assert r.returncode == 0

    # Verify final state
    state = json.loads((docs / "session_state.json").read_text())
    assert state["state"] == "SESSION_END"
    assert len(state["transitions"]) == 6  # START→ORIENT + 5 transitions
