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
    docs = tmp_path / "devlead_docs"
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
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _run(["start"], cwd=tmp_path)
    assert (docs / "session_state.json").exists()


def test_status_shows_state(tmp_path):
    """devlead status shows current state."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    _run(["start"], cwd=tmp_path)
    result = _run(["status"], cwd=tmp_path)
    assert result.returncode == 0
    assert "ORIENT" in result.stdout
    assert "Pipeline" in result.stdout


def test_status_no_session(tmp_path):
    """devlead status without start shows error."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    result = _run(["status"], cwd=tmp_path)
    assert result.returncode == 1
    assert "No active session" in result.stderr


def test_kpis_shows_dashboard(tmp_path):
    """devlead kpis shows full dashboard."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)

    result = _run(["kpis"], cwd=tmp_path)
    assert result.returncode == 0
    assert "LLM EFFECTIVENESS" in result.stdout
    assert "DELIVERY" in result.stdout
    assert "PROJECT HEALTH" in result.stdout


def test_gate_allows_in_orient(tmp_path):
    """devlead gate EXECUTE warns but allows in ORIENT state."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    _run(["start"], cwd=tmp_path)

    result = _run(["gate", "EXECUTE"], cwd=tmp_path)
    assert result.returncode == 0


def test_gate_allows_in_execute(tmp_path):
    """devlead gate EXECUTE allows after transitioning to EXECUTE."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    # Governance requires an active task
    (docs / "_project_tasks.md").write_text(
        "# Tasks\n\n> Type: PROJECT\n\n## Active\n\n"
        "| ID | Task | Story | Priority | Status | Assignee | Blockers |\n"
        "|----|----- |-------|----------|--------|----------|----------|\n"
        "| TASK-001 | Test | S-001 | P1 | IN_PROGRESS | claude | — |\n",
        encoding="utf-8",
    )
    _run(["start"], cwd=tmp_path)

    # Complete ORIENT checklist
    for key in ["status_read", "tasks_read", "intake_scanned", "kpis_reported"]:
        _run(["checklist", "ORIENT", key], cwd=tmp_path)
    # ORIENT → TRIAGE
    _run(["transition", "TRIAGE"], cwd=tmp_path)
    # Complete TRIAGE checklist
    for key in ["scratchpad_reviewed", "items_triaged"]:
        _run(["checklist", "TRIAGE", key], cwd=tmp_path)
    # TRIAGE → PRIORITIZE
    _run(["transition", "PRIORITIZE"], cwd=tmp_path)
    # Complete PRIORITIZE checklist
    for key in ["priorities_assigned", "session_scope_set"]:
        _run(["checklist", "PRIORITIZE", key], cwd=tmp_path)
    # PRIORITIZE → PLAN
    _run(["transition", "PLAN"], cwd=tmp_path)
    # PLAN → EXECUTE
    _run(["transition", "EXECUTE"], cwd=tmp_path)

    result = _run(["gate", "EXECUTE"], cwd=tmp_path)
    assert result.returncode == 0


def test_full_lifecycle(tmp_path):
    """Full state lifecycle: ORIENT → TRIAGE → PRIORITIZE → PLAN → EXECUTE → UPDATE → SESSION_END."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir()

    # Start
    r = _run(["start"], cwd=tmp_path)
    assert r.returncode == 0

    # ORIENT → TRIAGE
    for key in ["status_read", "tasks_read", "intake_scanned", "kpis_reported"]:
        _run(["checklist", "ORIENT", key], cwd=tmp_path)
    r = _run(["transition", "TRIAGE"], cwd=tmp_path)
    assert r.returncode == 0

    # TRIAGE → PRIORITIZE
    for key in ["scratchpad_reviewed", "items_triaged"]:
        _run(["checklist", "TRIAGE", key], cwd=tmp_path)
    r = _run(["transition", "PRIORITIZE"], cwd=tmp_path)
    assert r.returncode == 0

    # PRIORITIZE → PLAN
    for key in ["priorities_assigned", "session_scope_set"]:
        _run(["checklist", "PRIORITIZE", key], cwd=tmp_path)
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
    assert len(state["transitions"]) == 7  # START→ORIENT + 6 transitions (TRIAGE, PRIORITIZE added)
