"""Tests for workbook data model — BO dataclass and weight fields."""

from pathlib import Path

from devlead.workbook import BO, TBO, Story, Task, Workbook, load_workbook, _parse_bo_file


# ── Helpers ──────────────────────────────────────────────────


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _make_bo_file(docs_dir: Path) -> None:
    """Create _living_business_objectives.md with new BO format."""
    content = """# Business Objectives (TBOs)

> Type: LIVING

## Phase 1: MVP

| ID | Objective | Weight | Status |
|----|-----------|--------|--------|
| BO-1 | E2E governance works | 60 | FROZEN |
| BO-2 | Available on PyPI | 40 | FROZEN |

### BO-1: E2E governance works

| TBO | Description | Weight | DoD | Status |
|-----|-------------|--------|-----|--------|
| TBO-1 | Install and init | 50 | pip install works | DONE |
| TBO-2 | State lifecycle | 50 | 7-state lifecycle | IN_PROGRESS |

### BO-2: Available on PyPI

| TBO | Description | Weight | DoD | Status |
|-----|-------------|--------|-----|--------|
| TBO-3 | Package builds | 100 | twine upload works | DONE |
"""
    _write(docs_dir / "_living_business_objectives.md", content)


def _make_tbo_file(docs_dir: Path) -> None:
    """Create _living_business_objectives.md with old flat TBO format."""
    content = """# Business Objectives (TBOs)

> Type: LIVING

## TBO Tracker

| ID | Objective | Linked Stories | Status | Planned | Actual | Metric |
|----|-----------|---------------|--------|---------|--------|--------|
| TBO-1 | Single-project governance | S-001, S-002 | DONE | 2026-04-05 | 2026-04-05 | hooks fire |
| TBO-2 | Multi-project support | S-003 | IN_PROGRESS | 2026-04-10 | — | portfolio works |
"""
    _write(docs_dir / "_living_business_objectives.md", content)


def _make_story_file(docs_dir: Path) -> None:
    """Create _project_stories.md."""
    content = """# Stories

| ID | Story | Status | TBO Link | Epic |
|----|-------|--------|----------|------|
| S-001 | Init scaffold | DONE | TBO-1 | E-001 |
| S-002 | Hooks work | IN_PROGRESS | TBO-1 | E-001 |
| S-003 | Portfolio | OPEN | TBO-2 | E-002 |
"""
    _write(docs_dir / "_project_stories.md", content)


def _make_task_file(docs_dir: Path) -> None:
    """Create _project_tasks.md."""
    content = """# Tasks

| ID | Task | Status | Story | Priority | Assignee |
|----|------|--------|-------|----------|----------|
| TASK-001 | Build CLI | DONE | S-001 | P1 | claude |
| TASK-002 | Add hooks | IN_PROGRESS | S-002 | P1 | claude |
"""
    _write(docs_dir / "_project_tasks.md", content)


def test_bo_dataclass():
    bo = BO(id="BO-1", objective="E2E governance", weight=50, status="FROZEN", phase="Phase 1")
    assert bo.weight == 50
    assert bo.status == "FROZEN"
    assert bo.tbos == []


def test_tbo_has_weight():
    tbo = TBO(id="TBO-1", objective="Install works", status="DONE",
              planned="2026-04-05", actual="2026-04-05", metric="pip install works",
              weight=30, dod="pip install + init creates full scaffold")
    assert tbo.weight == 30
    assert tbo.dod == "pip install + init creates full scaffold"


def test_story_has_weight():
    s = Story(id="S-001", description="Package builds", epic_id="E-001",
              tbo_ids=["TBO-1"], status="DONE", dod="builds cleanly", weight=40)
    assert s.weight == 40


def test_workbook_has_bos():
    bo = BO(id="BO-1", objective="test", weight=100, status="FROZEN", phase="Phase 1")
    wb = Workbook(bos=[bo], tbos=[], shadow_tasks=[])
    assert len(wb.bos) == 1


def test_tbo_weight_defaults_to_zero():
    tbo = TBO(id="TBO-1", objective="test", status="OPEN")
    assert tbo.weight == 0
    assert tbo.dod == ""


def test_story_weight_defaults_to_zero():
    s = Story(id="S-001", description="test", epic_id="E-001")
    assert s.weight == 0


def test_workbook_bos_defaults_to_empty():
    wb = Workbook(tbos=[], shadow_tasks=[])
    assert wb.bos == []


# ── _parse_bo_file unit tests ────────────────────────────────


def test_parse_bo_file_extracts_bos():
    """Parse new BO format — extracts BO objects with phase and weight."""
    content = """# Business Objectives (TBOs)

> Type: LIVING

## Phase 1: MVP

| ID | Objective | Weight | Status |
|----|-----------|--------|--------|
| BO-1 | E2E governance works | 60 | FROZEN |
| BO-2 | Available on PyPI | 40 | FROZEN |

### BO-1: E2E governance works

| TBO | Description | Weight | DoD | Status |
|-----|-------------|--------|-----|--------|
| TBO-1 | Install and init | 50 | pip install works | DONE |
| TBO-2 | State lifecycle | 50 | 7-state lifecycle | IN_PROGRESS |

### BO-2: Available on PyPI

| TBO | Description | Weight | DoD | Status |
|-----|-------------|--------|-----|--------|
| TBO-3 | Package builds | 100 | twine upload works | DONE |
"""
    bos = _parse_bo_file(content)
    assert len(bos) == 2
    assert bos[0].id == "BO-1"
    assert bos[0].objective == "E2E governance works"
    assert bos[0].weight == 60
    assert bos[0].status == "FROZEN"
    assert bos[0].phase == "Phase 1: MVP"
    assert len(bos[0].tbos) == 2
    assert bos[0].tbos[0].id == "TBO-1"
    assert bos[0].tbos[0].objective == "Install and init"
    assert bos[0].tbos[0].weight == 50
    assert bos[0].tbos[0].dod == "pip install works"
    assert bos[0].tbos[0].status == "DONE"
    assert bos[0].tbos[1].id == "TBO-2"
    assert bos[0].tbos[1].status == "IN_PROGRESS"
    assert bos[1].id == "BO-2"
    assert bos[1].weight == 40
    assert len(bos[1].tbos) == 1
    assert bos[1].tbos[0].id == "TBO-3"
    assert bos[1].tbos[0].weight == 100
    assert bos[1].tbos[0].dod == "twine upload works"


def test_parse_bo_file_empty():
    """Empty text returns empty list."""
    assert _parse_bo_file("") == []


# ── Integration tests with load_workbook ─────────────────────


def test_load_workbook_with_bos(tmp_docs):
    """New BO format loads BOs with nested TBOs."""
    _make_bo_file(tmp_docs)
    _make_story_file(tmp_docs)
    _make_task_file(tmp_docs)
    wb = load_workbook(tmp_docs)
    assert len(wb.bos) == 2
    assert wb.bos[0].id == "BO-1"
    assert wb.bos[0].weight == 60
    assert wb.bos[0].status == "FROZEN"
    assert wb.bos[0].phase == "Phase 1: MVP"
    assert len(wb.bos[0].tbos) == 2
    assert wb.bos[0].tbos[0].id == "TBO-1"
    assert wb.bos[0].tbos[0].weight == 50
    assert wb.bos[0].tbos[0].dod == "pip install works"
    assert wb.bos[1].id == "BO-2"
    assert len(wb.bos[1].tbos) == 1
    # Flat tbos list also populated for backward compat
    assert len(wb.tbos) == 3


def test_load_workbook_backward_compat(tmp_docs):
    """Old format (flat TBO list) still loads — wraps in default BO."""
    _make_tbo_file(tmp_docs)
    _make_story_file(tmp_docs)
    _make_task_file(tmp_docs)
    wb = load_workbook(tmp_docs)
    assert len(wb.bos) >= 1
    assert wb.bos[0].status == "DRAFT"
    assert len(wb.tbos) > 0
    # Weights should sum to 100
    total_weight = sum(t.weight for t in wb.tbos)
    assert total_weight == 100


def test_load_workbook_no_bo_file(tmp_docs):
    """No BO file at all — empty bos and tbos."""
    _make_story_file(tmp_docs)
    _make_task_file(tmp_docs)
    wb = load_workbook(tmp_docs)
    assert wb.bos == []
    assert wb.tbos == []
