"""Tests for the convergence-layer schema extensions on BO and TTO.

Part of FEATURES-0014. Verifies:
  - new BO fields (metric, baseline, target, metric_source, current) parse
  - new TTO fields (intent_vector, verify_kind) parse from indented subfields
  - BO.has_metric_source and BO.normalised_progress derived properties
  - backward compat — hierarchies without the new fields still parse cleanly
"""
from __future__ import annotations

import math
from pathlib import Path
import pytest

from devlead.hierarchy import BO, TTO, parse


# --- BO derived properties -------------------------------------------------

def test_bo_has_metric_source_false_when_default():
    bo = BO(id="BO-1", name="x", weight=30)
    assert bo.has_metric_source is False

def test_bo_has_metric_source_false_when_partial():
    # metric set but no metric_source
    bo = BO(id="BO-1", name="x", weight=30,
            metric="signups", baseline=0.0, target=50.0)
    assert bo.has_metric_source is False

def test_bo_has_metric_source_true_when_complete():
    bo = BO(id="BO-1", name="x", weight=30,
            metric="signups", baseline=0.0, target=50.0,
            metric_source="manual")
    assert bo.has_metric_source is True

def test_bo_normalised_progress_none_without_current():
    bo = BO(id="BO-1", name="x", weight=30,
            metric="signups", baseline=0.0, target=50.0,
            metric_source="manual")
    assert bo.normalised_progress is None

def test_bo_normalised_progress_at_baseline_is_zero():
    bo = BO(id="BO-1", name="x", weight=30,
            metric="signups", baseline=0.0, target=50.0,
            metric_source="manual", current=0.0)
    assert bo.normalised_progress == 0.0

def test_bo_normalised_progress_at_target_is_one():
    bo = BO(id="BO-1", name="x", weight=30,
            metric="signups", baseline=0.0, target=50.0,
            metric_source="manual", current=50.0)
    assert bo.normalised_progress == 1.0

def test_bo_normalised_progress_inverted_axis():
    # smaller-is-better: baseline 600s, target 60s, current 240s
    # progress = (240 - 600) / (60 - 600) = -360 / -540 ≈ 0.667
    bo = BO(id="BO-2", name="x", weight=20,
            metric="latency_ms", baseline=600.0, target=60.0,
            metric_source="shell:curl latency", current=240.0)
    assert math.isclose(bo.normalised_progress, 360 / 540, abs_tol=1e-12)

def test_bo_normalised_progress_zero_displacement():
    bo = BO(id="BO-1", name="x", weight=30,
            metric="x", baseline=5.0, target=5.0,
            metric_source="manual", current=5.0)
    assert bo.normalised_progress == 1.0


# --- TTO defaults ----------------------------------------------------------

def test_tto_intent_vector_defaults_empty():
    tto = TTO(id="TTO-1", name="x", weight=10, done=False)
    assert tto.intent_vector == {}

def test_tto_verify_kind_defaults_shell():
    tto = TTO(id="TTO-1", name="x", weight=10, done=False)
    assert tto.verify_kind == "shell"


# --- parser: new BO fields -------------------------------------------------

def test_parse_bo_with_metric_fields(tmp_path: Path):
    text = """## Sprint 1 — Test Sprint

### BO-1: Some objective (weight: 30)
- **metric:** weekly trial signups
- **baseline:** 0
- **target:** 50
- **metric_source:** manual
- **current:** 12

#### TBO-1.1: A theme (weight: 100)
- [ ] TTO-1.1.1: Some task (weight: 50) [functional]
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    sprints = parse(p)
    bo = sprints[0].bos[0]
    assert bo.metric == "weekly trial signups"
    assert bo.baseline == 0.0
    assert bo.target == 50.0
    assert bo.metric_source == "manual"
    assert bo.current == 12.0
    assert bo.has_metric_source is True
    assert math.isclose(bo.normalised_progress, 12 / 50, abs_tol=1e-12)


def test_parse_bo_legacy_no_metric_fields(tmp_path: Path):
    """Backward compat: hierarchies without metric fields parse cleanly."""
    text = """## Sprint 1 — Test Sprint

### BO-1: Legacy objective (weight: 40)
- **start_date:** 2026-04-16
- **end_date:** 2026-04-28

#### TBO-1.1: A theme (weight: 100)
- [ ] TTO-1.1.1: Some task (weight: 50) [functional]
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    sprints = parse(p)
    bo = sprints[0].bos[0]
    assert bo.metric == ""
    assert bo.baseline is None
    assert bo.target is None
    assert bo.has_metric_source is False
    assert bo.normalised_progress is None


def test_parse_bo_invalid_baseline_silently_skipped(tmp_path: Path):
    """Malformed numeric value leaves field at default — no crash."""
    text = """## Sprint 1 — Test

### BO-1: x (weight: 30)
- **baseline:** not-a-number
- **target:** 100

#### TBO-1.1: t (weight: 100)
- [ ] TTO-1.1.1: a (weight: 100) [functional]
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    bo = parse(p)[0].bos[0]
    assert bo.baseline is None  # skipped on parse error
    assert bo.target == 100.0   # other field still parsed


# --- parser: new TTO subfields ---------------------------------------------

def test_parse_tto_with_intent_vector(tmp_path: Path):
    text = """## Sprint 1 — Test

### BO-1: x (weight: 30)

#### TBO-1.1: t (weight: 100)
- [ ] TTO-1.1.1: First task (weight: 40) [functional]
  - **intent:** BO-1: 0.40, BO-3: 0.05
  - **verify_kind:** shell
- [ ] TTO-1.1.2: Second task (weight: 60) [non-functional]
  - **intent_vector:** BO-2: 0.30
  - **verify_kind:** benchmark
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    sprints = parse(p)
    ttos = sprints[0].bos[0].tbos[0].ttos
    assert ttos[0].intent_vector == {"BO-1": 0.40, "BO-3": 0.05}
    assert ttos[0].verify_kind == "shell"
    assert ttos[1].intent_vector == {"BO-2": 0.30}
    assert ttos[1].verify_kind == "benchmark"


def test_parse_tto_legacy_no_subfields(tmp_path: Path):
    """Backward compat: existing TTOs without subfields use defaults."""
    text = """## Sprint 1 — Test

### BO-1: x (weight: 30)

#### TBO-1.1: t (weight: 100)
- [ ] TTO-1.1.1: A (weight: 50) [functional]
  verify: echo hello
- [x] TTO-1.1.2: B (weight: 50) [functional]
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    ttos = parse(p)[0].bos[0].tbos[0].ttos
    assert all(t.intent_vector == {} for t in ttos)
    assert all(t.verify_kind == "shell" for t in ttos)


def test_parse_existing_devlead_hierarchy_does_not_crash():
    """Smoke test: the live _project_hierarchy.md must still parse."""
    p = Path(__file__).resolve().parents[1] / "devlead_docs" / "_project_hierarchy.md"
    if not p.exists():
        pytest.skip("live hierarchy file not present")
    sprints = parse(p)
    assert len(sprints) >= 1
    # Every BO present should still have id/name/weight even without new fields.
    for s in sprints:
        for bo in s.bos:
            assert bo.id.startswith("BO-")
            assert bo.weight > 0


def test_parse_intent_vector_handles_messy_whitespace(tmp_path: Path):
    text = """## Sprint 1 — Test

### BO-1: x (weight: 30)

#### TBO-1.1: t (weight: 100)
- [ ] TTO-1.1.1: A (weight: 50) [functional]
  - **intent:**   BO-1:  0.40 ,  BO-3 :0.05  ,
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    tto = parse(p)[0].bos[0].tbos[0].ttos[0]
    assert tto.intent_vector == {"BO-1": 0.40, "BO-3": 0.05}


def test_parse_intent_vector_skips_malformed_entries(tmp_path: Path):
    text = """## Sprint 1 — Test

### BO-1: x (weight: 30)

#### TBO-1.1: t (weight: 100)
- [ ] TTO-1.1.1: A (weight: 50) [functional]
  - **intent:** BO-1: 0.40, garbage-no-colon, BO-3: not-a-float, BO-4: 0.20
"""
    p = tmp_path / "_project_hierarchy.md"
    p.write_text(text, encoding="utf-8")
    tto = parse(p)[0].bos[0].tbos[0].ttos[0]
    assert tto.intent_vector == {"BO-1": 0.40, "BO-4": 0.20}
