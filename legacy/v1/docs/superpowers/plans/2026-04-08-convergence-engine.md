# Business Convergence Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add weighted Business Objective → TBO → Story hierarchy with convergence formula, 6 KPI instruments, and CLAUDE.md model-ownership instructions.

**Architecture:** Extend existing workbook.py with BO dataclass and weight fields. New convergence.py computes weighted sums. Existing kpi_engine.py gets 6 new business KPI instruments. CLAUDE.md scaffold gets model-ownership behavior instructions.

**Tech Stack:** Python 3.11+ stdlib only. Markdown tables. TOML config.

---

### Task 1: Extend Data Model — BO dataclass + weights on TBO/Story (TASK-075)

**Files:**
- Modify: `src/devlead/workbook.py`
- Test: `tests/test_workbook.py`

**Current state:** Workbook has `tbos: list[TBO]`, `shadow_tasks: list[Task]`. TBO has no weight. Story has no weight. No BO concept.

- [ ] **Step 1: Write failing tests for BO and weighted TBO/Story**

```python
# tests/test_workbook.py — add these tests

def test_bo_dataclass():
    from devlead.workbook import BO
    bo = BO(id="BO-1", objective="E2E governance", weight=50, status="FROZEN", phase="Phase 1")
    assert bo.weight == 50
    assert bo.status == "FROZEN"

def test_tbo_has_weight():
    from devlead.workbook import TBO
    tbo = TBO(id="TBO-1", objective="Install works", status="DONE",
              planned="2026-04-05", actual="2026-04-05", metric="pip install works",
              weight=30, dod="pip install + init creates full scaffold")
    assert tbo.weight == 30
    assert tbo.dod == "pip install + init creates full scaffold"

def test_story_has_weight():
    from devlead.workbook import Story
    s = Story(id="S-001", description="Package builds", epic_id="E-001",
              tbo_ids=["TBO-1"], status="DONE", dod="builds cleanly", weight=40)
    assert s.weight == 40

def test_workbook_has_bos():
    from devlead.workbook import Workbook, BO
    bo = BO(id="BO-1", objective="test", weight=100, status="FROZEN", phase="Phase 1")
    wb = Workbook(bos=[bo], tbos=[], shadow_tasks=[])
    assert len(wb.bos) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_workbook.py -v -k "bo_dataclass or tbo_has_weight or story_has_weight or workbook_has_bos"`
Expected: ImportError or AttributeError — BO doesn't exist, weight field missing

- [ ] **Step 3: Add BO dataclass and weight fields**

In `src/devlead/workbook.py`, add:

```python
@dataclass
class BO:
    """Business Objective — phase-scoped, frozen when accepted."""
    id: str
    objective: str
    weight: int  # out of 100 for the phase
    status: str  # DRAFT, FROZEN, DONE
    phase: str
    tbos: list['TBO'] = field(default_factory=list)
```

Add to TBO dataclass:
```python
    weight: int = 0       # out of 100 for its BO
    dod: str = ""         # Definition of Done
```

Add to Story dataclass:
```python
    weight: int = 0       # out of 100 for its TBO
```

Add to Workbook dataclass:
```python
    bos: list[BO] = field(default_factory=list)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_workbook.py -v`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add src/devlead/workbook.py tests/test_workbook.py
git commit -m "feat: add BO dataclass, weight fields on TBO/Story"
```

---

### Task 2: Parse new BO file format from `_living_business_objectives.md` (TASK-075)

**Files:**
- Modify: `src/devlead/workbook.py` (load_workbook function)
- Test: `tests/test_workbook.py`

**Current format:** Flat TBO table with columns: ID, Objective, Linked Stories, Status, Planned, Actual, Metric.
**New format:** Phase header → BO table → per-BO TBO subtables (Section 9.2 of spec).

- [ ] **Step 1: Write failing test for BO parsing**

```python
def _make_bo_file(docs_dir):
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
    (docs_dir / "_living_business_objectives.md").write_text(content)


def test_load_workbook_with_bos(tmp_docs):
    _make_bo_file(tmp_docs)
    _make_story_file(tmp_docs)  # reuse existing helper
    _make_task_file(tmp_docs)   # reuse existing helper
    wb = load_workbook(tmp_docs)
    assert len(wb.bos) == 2
    assert wb.bos[0].id == "BO-1"
    assert wb.bos[0].weight == 60
    assert wb.bos[0].status == "FROZEN"
    assert wb.bos[0].phase == "Phase 1: MVP"
    assert len(wb.bos[0].tbos) == 2
    assert wb.bos[0].tbos[0].weight == 50

def test_load_workbook_backward_compat(tmp_docs):
    """Old format (flat TBO list) still loads — wraps in default BO."""
    _make_tbo_file(tmp_docs)  # old format helper
    _make_story_file(tmp_docs)
    _make_task_file(tmp_docs)
    wb = load_workbook(tmp_docs)
    # Should have 1 default BO wrapping all TBOs
    assert len(wb.bos) >= 1
    assert len(wb.tbos) > 0  # backward compat: tbos still populated
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement BO parsing in load_workbook**

Add `_parse_bo_file(text: str) -> tuple[list[BO], str]` function that:
1. Finds `## Phase N:` headers to get phase name
2. Parses the BO table (ID, Objective, Weight, Status)
3. For each BO, finds `### BO-N:` section and parses TBO subtable
4. Returns list of BOs with their TBOs populated, plus phase name

Update `load_workbook()` to:
1. Try new BO format first
2. If no BOs found, fall back to old flat TBO parsing
3. If old format, wrap TBOs in a default BO with equal weights
4. Populate `wb.bos` and `wb.tbos` (backward compat)

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

### Task 3: Create convergence.py — weighted convergence formula (TASK-075)

**Files:**
- Create: `src/devlead/convergence.py`
- Test: `tests/test_convergence.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_convergence.py

from devlead.convergence import (
    story_convergence,
    tbo_convergence,
    bo_convergence,
    phase_convergence,
)
from devlead.workbook import BO, TBO, Story, Task


def test_story_convergence_done():
    assert story_convergence("DONE") == 1.0

def test_story_convergence_not_done():
    assert story_convergence("IN_PROGRESS") == 0.0

def test_tbo_convergence_all_done():
    stories = [
        Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=60),
        Story(id="S-2", description="b", epic_id="", tbo_ids=[], status="DONE", dod="", weight=40),
    ]
    tbo = TBO(id="TBO-1", objective="x", status="DONE", planned="", actual="", metric="", weight=50, dod="", stories=stories)
    assert tbo_convergence(tbo) == 100.0

def test_tbo_convergence_partial():
    stories = [
        Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=60),
        Story(id="S-2", description="b", epic_id="", tbo_ids=[], status="IN_PROGRESS", dod="", weight=40),
    ]
    tbo = TBO(id="TBO-1", objective="x", status="IN_PROGRESS", planned="", actual="", metric="", weight=50, dod="", stories=stories)
    assert tbo_convergence(tbo) == 60.0

def test_bo_convergence():
    s1 = Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=100)
    s2 = Story(id="S-2", description="b", epic_id="", tbo_ids=[], status="IN_PROGRESS", dod="", weight=100)
    tbo1 = TBO(id="TBO-1", objective="x", status="DONE", planned="", actual="", metric="", weight=30, dod="", stories=[s1])
    tbo2 = TBO(id="TBO-2", objective="y", status="IP", planned="", actual="", metric="", weight=70, dod="", stories=[s2])
    bo = BO(id="BO-1", objective="test", weight=100, status="FROZEN", phase="P1", tbos=[tbo1, tbo2])
    # BO conv = (30*100 + 70*0) / 100 = 30.0
    assert bo_convergence(bo) == 30.0

def test_phase_convergence():
    s1 = Story(id="S-1", description="a", epic_id="", tbo_ids=[], status="DONE", dod="", weight=100)
    tbo1 = TBO(id="TBO-1", objective="x", status="DONE", planned="", actual="", metric="", weight=100, dod="", stories=[s1])
    bo1 = BO(id="BO-1", objective="a", weight=60, status="FROZEN", phase="P1", tbos=[tbo1])
    bo2 = BO(id="BO-2", objective="b", weight=40, status="FROZEN", phase="P1", tbos=[])
    # Phase = (60*100 + 40*0) / 100 = 60.0
    assert phase_convergence([bo1, bo2]) == 60.0

def test_phase_convergence_empty():
    assert phase_convergence([]) == 0.0

def test_tbo_convergence_no_stories():
    tbo = TBO(id="TBO-1", objective="x", status="NOT_STARTED", planned="", actual="", metric="", weight=50, dod="")
    assert tbo_convergence(tbo) == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

- [ ] **Step 3: Implement convergence.py**

```python
"""Weighted convergence engine for DevLead.

Computes business convergence as weighted sums rolling up from
Story → TBO → BO → Phase.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devlead.workbook import BO, TBO


def story_convergence(status: str) -> float:
    """Binary: 1.0 if DONE, 0.0 otherwise."""
    return 1.0 if "DONE" in status.upper() else 0.0


def tbo_convergence(tbo: TBO) -> float:
    """Weighted sum of story completion within a TBO. Returns 0-100."""
    if not tbo.stories:
        return 0.0
    total = sum(s.weight * story_convergence(s.status) for s in tbo.stories)
    weight_sum = sum(s.weight for s in tbo.stories)
    return (total / weight_sum * 100) if weight_sum > 0 else 0.0


def bo_convergence(bo: BO) -> float:
    """Weighted sum of TBO convergence within a BO. Returns 0-100."""
    if not bo.tbos:
        return 0.0
    total = sum(t.weight * tbo_convergence(t) for t in bo.tbos)
    weight_sum = sum(t.weight for t in bo.tbos)
    return (total / weight_sum) if weight_sum > 0 else 0.0


def phase_convergence(bos: list[BO]) -> float:
    """Weighted sum of BO convergence across a phase. Returns 0-100."""
    if not bos:
        return 0.0
    total = sum(b.weight * bo_convergence(b) for b in bos)
    weight_sum = sum(b.weight for b in bos)
    return (total / weight_sum) if weight_sum > 0 else 0.0


def coverage_score(bo: BO) -> float:
    """What % of BO weight has TBOs defined. Returns 0-100."""
    if not bo.tbos:
        return 0.0
    return min(sum(t.weight for t in bo.tbos), 100)


def traceability_score(total_tasks: int, traced_tasks: int) -> float:
    """% of tasks that trace to a BO. Returns 0-100."""
    if total_tasks == 0:
        return 100.0
    return traced_tasks / total_tasks * 100
```

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

---

### Task 4: Wire convergence into CLI status + dashboard (TASK-077)

**Files:**
- Modify: `src/devlead/cli.py` (_cmd_status)
- Modify: `src/devlead/dashboard.py` (_tab_business)
- Test: Manual verification via `devlead status` and `devlead dashboard`

- [ ] **Step 1: Update _cmd_status in cli.py**

Import convergence functions. After loading workbook, compute and display:
```
Phase 1: 62% converged
  BO-1: E2E governance (60%) — 85% converged
  BO-2: PyPI distribution (40%) — 30% converged
```

- [ ] **Step 2: Update _tab_business in dashboard.py**

Replace the current TBO dump with:
- Phase convergence bar (0-100)
- Per-BO convergence with weight labels
- Per-TBO convergence nested under each BO

- [ ] **Step 3: Run full test suite**

Run: `python -m pytest tests/ -v`

- [ ] **Step 4: Commit**

---

### Task 5: 6 KPI instruments in kpi_engine.py (TASK-076)

**Files:**
- Modify: `src/devlead/kpi_engine.py`
- Test: `tests/test_kpi_engine.py` (add tests for new KPIs)

Add 6 new KPIs to `compute_builtin_kpis()` as a new category "D: Business Convergence":

- [ ] **Step 1: Write failing tests for each KPI**

Test each KPI returns a KpiResult with expected value given known inputs.

- [ ] **Step 2: Implement KPI D1: Convergence**
- Phase convergence from workbook BOs
- Per-BO breakdown in detail string

- [ ] **Step 3: Implement KPI D2: Going in Circles**
- Zero-delta sessions from session_history.jsonl
- Rework detection (story status regression)

- [ ] **Step 4: Implement KPI D3: Skin in the Game**
- Traceability = traced_tasks / total_tasks
- Coverage = mean of coverage_score across BOs

- [ ] **Step 5: Implement KPI D4: Time Investment**
- Effort vs weight ratio per TBO from effort log

- [ ] **Step 6: Implement KPI D5: Tokenomics**
- Tokens per convergence point from session history

- [ ] **Step 7: Implement KPI D6: Shadow Work**
- Shadow ratio = shadow_tasks / total_tasks

- [ ] **Step 8: Run full test suite**

- [ ] **Step 9: Commit**

---

### Task 6: Migration — extend devlead migrate for BO format (TASK-077)

**Files:**
- Modify: `src/devlead/migrate.py`
- Modify: `src/devlead/scaffold/_living_business_objectives.md`
- Create: `src/devlead/scaffold/_living_vision.md`
- Test: `tests/test_init.py` or `tests/test_migrate.py`

- [ ] **Step 1: Create _living_vision.md scaffold template**

```markdown
# Product Vision

> Type: LIVING
> Last updated: {date}

<!-- Replace with your product's north star. A few lines of English. -->
<!-- This never changes unless the product fundamentally pivots. -->
```

- [ ] **Step 2: Update _living_business_objectives.md scaffold template**

Replace flat TBO format with new BO → TBO format from spec Section 9.2.

- [ ] **Step 3: Update migrate.py EXPECTED_FILES list**

Add `_living_vision.md` to the expected files.

- [ ] **Step 4: Add BO migration logic**

When `devlead migrate` detects an old-format `_living_business_objectives.md` (flat TBO table), transform it:
1. Wrap all TBOs under a default BO with weight 100
2. Assign equal weights to TBOs (100 / N)
3. Mark BO as DRAFT
4. Write new format

- [ ] **Step 5: Run tests**

- [ ] **Step 6: Commit**

---

### Task 7: CLAUDE.md scaffold — model ownership behavior (TASK-078)

**Files:**
- Modify: `src/devlead/scaffold/_living_standing_instructions.md`
- Modify: `src/devlead/migrate.py` (CLAUDE.md section)

- [ ] **Step 1: Add model ownership instructions to standing instructions scaffold**

Add section to the scaffold template:

```markdown
## Model Ownership — "I won't fly in the dark"

21. **The model owns the business-to-technical mapping.** Before recommending work, the model must be able to trace it to a Business Objective. If it can't, it says "I won't fly in the dark" and explains what's missing.

22. **Three confidence levels:**
    - **"I own this"** — Vision + frozen BOs + TBO decomposition exists. Report convergence, recommend work.
    - **"I can see the runway"** — BOs exist but TBOs not decomposed. Can do requested work, proactively decompose.
    - **"I won't fly in the dark"** — No BOs defined. Must interview user or synthesize from codebase before recommending priorities.

23. **Model owns TBO decomposition after BO freeze.** Adding a TBO after freeze = scope change. Flag explicitly.

24. **At session start, read the instrument panel.** Report phase convergence, per-BO convergence, shadow ratio, and recommended next work with traceability. Use `devlead status` output.
```

- [ ] **Step 2: Update CLAUDE.md section in migrate.py**

Add to the CLAUDE.md section that migrate appends:
```
## Business Convergence
- Run `devlead status` at session start to see convergence
- Check `devlead_docs/_living_business_objectives.md` for BOs and TBOs
- Every task must trace to a BO. Untraced work is shadow work.
- If no BOs are defined, interview the user before proposing work priorities.
```

- [ ] **Step 3: Commit**

---

### Task 8: Verification — end-to-end test (all tasks)

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest tests/ -v
```

- [ ] **Step 2: Test on live project (dogfood)**

```bash
devlead status     # Should show weighted convergence
devlead dashboard  # Should show BO-based Business tab
devlead view       # Should show BO → TBO → Story hierarchy
```

- [ ] **Step 3: Verify backward compatibility**

Old-format `_living_business_objectives.md` files should still load (wrapped in default BO).

- [ ] **Step 4: Final commit**
