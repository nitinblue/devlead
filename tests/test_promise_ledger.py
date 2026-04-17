"""Tests for src/devlead/promise_ledger.py.

Part of FEATURES-0014 Step 5. Verifies the writer side of the promise ledger:
  - append_promise writes a single row
  - read_all reads cleanly, skips malformed lines
  - collect_bo_metrics snapshots BO.current values
  - write_promises_for skips TTOs without intent_vector
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from devlead.hierarchy import BO, TBO, TTO, Sprint
from devlead.promise_ledger import (
    DEFAULT_WINDOW_DAYS,
    append_promise,
    collect_bo_metrics,
    read_all,
    write_promises_for,
)


# --- append_promise --------------------------------------------------------

def test_append_promise_writes_one_row(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    row = append_promise(
        ledger_path=p,
        tto_id="TTO-1",
        promised={"BO-1": 0.40},
        bo_metrics_at_done={"BO-1": 0.0},
    )
    assert row["tto_id"] == "TTO-1"
    assert row["status"] == "pending"
    assert row["window_days"] == DEFAULT_WINDOW_DAYS
    assert row["realised"] is None
    assert p.exists()
    assert len(p.read_text(encoding="utf-8").splitlines()) == 1


def test_append_promise_creates_parent_dir(tmp_path: Path):
    p = tmp_path / "nested" / "subdir" / "_promise_ledger.jsonl"
    append_promise(p, "TTO-1", {"BO-1": 0.1}, {"BO-1": 0.0})
    assert p.exists()


def test_append_promise_appends_not_overwrites(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    append_promise(p, "TTO-1", {"BO-1": 0.1}, {"BO-1": 0.0})
    append_promise(p, "TTO-2", {"BO-2": 0.2}, {"BO-2": 0.0})
    rows = read_all(p)
    assert len(rows) == 2
    assert rows[0]["tto_id"] == "TTO-1"
    assert rows[1]["tto_id"] == "TTO-2"


def test_append_promise_explicit_timestamp(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    row = append_promise(
        p, "TTO-1", {"BO-1": 0.1}, {"BO-1": 0.0},
        verified_done_at="2026-04-17T12:00:00Z",
    )
    assert row["verified_done_at"] == "2026-04-17T12:00:00Z"


def test_append_promise_custom_window(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    row = append_promise(
        p, "TTO-1", {"BO-1": 0.1}, {"BO-1": 0.0},
        window_days=14,
    )
    assert row["window_days"] == 14


# --- read_all --------------------------------------------------------------

def test_read_all_missing_file_returns_empty(tmp_path: Path):
    assert read_all(tmp_path / "nonexistent.jsonl") == []


def test_read_all_skips_malformed_lines(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    p.write_text(
        '{"tto_id": "T1", "status": "pending"}\n'
        'this is not json\n'
        '\n'  # blank line, also fine
        '{"tto_id": "T2", "status": "pending"}\n',
        encoding="utf-8",
    )
    rows = read_all(p)
    assert [r["tto_id"] for r in rows] == ["T1", "T2"]


# --- collect_bo_metrics ----------------------------------------------------

def _make_sprints_for_metrics_test() -> list[Sprint]:
    bo1 = BO(id="BO-1", name="x", weight=30, current=12.0)
    bo2 = BO(id="BO-2", name="y", weight=30)  # no current declared
    sprint = Sprint(name="S1", bos=[bo1, bo2])
    return [sprint]


def test_collect_bo_metrics_snapshots_current_values():
    sprints = _make_sprints_for_metrics_test()
    snap = collect_bo_metrics(sprints)
    assert snap == {"BO-1": 12.0, "BO-2": None}


# --- write_promises_for ----------------------------------------------------

def _make_sprints_with_intent() -> list[Sprint]:
    tto_a = TTO(id="TTO-A", name="a", weight=50, done=True,
                intent_vector={"BO-1": 0.40})
    tto_b = TTO(id="TTO-B", name="b", weight=50, done=True,
                intent_vector={})  # infrastructural
    tto_c = TTO(id="TTO-C", name="c", weight=50, done=True,
                intent_vector={"BO-1": 0.10, "BO-2": 0.20})
    tbo = TBO(id="TBO-1", name="t", weight=100, ttos=[tto_a, tto_b, tto_c])
    bo1 = BO(id="BO-1", name="x", weight=30, current=5.0, tbos=[tbo])
    bo2 = BO(id="BO-2", name="y", weight=30, current=10.0)
    return [Sprint(name="S1", bos=[bo1, bo2])]


def test_write_promises_for_writes_one_row_per_tto_with_intent(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    sprints = _make_sprints_with_intent()
    written = write_promises_for(p, sprints, ["TTO-A", "TTO-B", "TTO-C"])
    # TTO-B has no intent_vector → skipped
    assert {row["tto_id"] for row in written} == {"TTO-A", "TTO-C"}
    rows = read_all(p)
    assert len(rows) == 2


def test_write_promises_for_includes_metric_snapshot(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    sprints = _make_sprints_with_intent()
    written = write_promises_for(p, sprints, ["TTO-A"])
    row = written[0]
    assert row["bo_metrics_at_done"] == {"BO-1": 5.0, "BO-2": 10.0}
    assert row["promised"] == {"BO-1": 0.40}


def test_write_promises_for_unknown_tto_id_silently_skipped(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    sprints = _make_sprints_with_intent()
    written = write_promises_for(p, sprints, ["TTO-DOES-NOT-EXIST"])
    assert written == []
    assert read_all(p) == []


def test_write_promises_for_empty_id_list_no_op(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    sprints = _make_sprints_with_intent()
    written = write_promises_for(p, sprints, [])
    assert written == []
    assert not p.exists()


# --- realisation sweep ----------------------------------------------------

from datetime import datetime, timezone, timedelta

from devlead.promise_ledger import (
    PHI_REALISED_THRESHOLD,
    PHI_VAPOR_THRESHOLD,
    run_realisation_sweep,
)


def _sprints_for_sweep(bo_currents: dict[str, float]) -> list[Sprint]:
    """Build a sprint with two measurable BOs at the given current values."""
    bo1 = BO(id="BO-1", name="x", weight=30,
             metric="m", baseline=0.0, target=10.0, metric_source="manual",
             current=bo_currents.get("BO-1", 0.0))
    bo2 = BO(id="BO-2", name="y", weight=20,
             metric="n", baseline=0.0, target=5.0, metric_source="manual",
             current=bo_currents.get("BO-2", 0.0))
    return [Sprint(name="S1", bos=[bo1, bo2])]


def test_realisation_sweep_no_pending_rows_returns_zeros(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    result = run_realisation_sweep(p, _sprints_for_sweep({}))
    assert result == {"checked": 0, "updated": 0, "skipped_no_data": 0}


def test_realisation_sweep_skips_unexpired_window(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    now = datetime(2026, 4, 17, 12, 0, 0, tzinfo=timezone.utc)
    # promise made today, window 7 days — not yet expired
    append_promise(
        p, "TTO-A", {"BO-1": 0.40},
        bo_metrics_at_done={"BO-1": 0.0, "BO-2": 0.0},
        verified_done_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        window_days=7,
    )
    result = run_realisation_sweep(p, _sprints_for_sweep({"BO-1": 4.0}), now=now)
    assert result["checked"] == 0  # skipped due to window
    rows = read_all(p)
    assert rows[0]["status"] == "pending"


def test_realisation_sweep_realised_when_phi_high(tmp_path: Path):
    """φ >= PHI_REALISED_THRESHOLD ⇒ status = 'realised'."""
    p = tmp_path / "_promise_ledger.jsonl"
    promise_time = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
    sweep_time = promise_time + timedelta(days=10)  # window passed
    append_promise(
        p, "TTO-A", {"BO-1": 0.40},  # promised 0.40 normalised on BO-1
        bo_metrics_at_done={"BO-1": 0.0, "BO-2": 0.0},
        verified_done_at=promise_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        window_days=7,
    )
    # BO-1 baseline=0, target=10, current=4 ⇒ normalised change = 4/10 = 0.40
    sprints = _sprints_for_sweep({"BO-1": 4.0})
    result = run_realisation_sweep(p, sprints, now=sweep_time)
    assert result["updated"] == 1
    rows = read_all(p)
    assert rows[0]["status"] == "realised"
    # φ = (r·i)/(i·i) = (0.40*0.40)/(0.40*0.40) = 1.0
    assert math.isclose(rows[0]["phi"], 1.0, abs_tol=1e-9)
    assert math.isclose(rows[0]["epsilon"], 1.0, abs_tol=1e-9)


def test_realisation_sweep_vapor_when_phi_below_vapor_threshold(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    promise_time = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
    sweep_time = promise_time + timedelta(days=10)
    append_promise(
        p, "TTO-A", {"BO-1": 0.40},
        bo_metrics_at_done={"BO-1": 0.0, "BO-2": 0.0},
        verified_done_at=promise_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        window_days=7,
    )
    # BO-1 actually moved 0.5 (5% of 10 displacement) — far less than promised 40%
    sprints = _sprints_for_sweep({"BO-1": 0.5})
    result = run_realisation_sweep(p, sprints, now=sweep_time)
    assert result["updated"] == 1
    rows = read_all(p)
    # φ = (0.05 * 0.40) / (0.40 * 0.40) = 0.125 < PHI_VAPOR_THRESHOLD (0.30)
    assert rows[0]["phi"] < PHI_VAPOR_THRESHOLD
    assert rows[0]["status"] == "vapor"


def test_realisation_sweep_partial_in_between(tmp_path: Path):
    p = tmp_path / "_promise_ledger.jsonl"
    promise_time = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
    sweep_time = promise_time + timedelta(days=10)
    append_promise(
        p, "TTO-A", {"BO-1": 0.40},
        bo_metrics_at_done={"BO-1": 0.0, "BO-2": 0.0},
        verified_done_at=promise_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        window_days=7,
    )
    # Realised 50% of promised: current = 2.0 ⇒ normalised 0.20
    # φ = (0.20 * 0.40) / 0.16 = 0.5  → between thresholds → "partial"
    sprints = _sprints_for_sweep({"BO-1": 2.0})
    run_realisation_sweep(p, sprints, now=sweep_time)
    rows = read_all(p)
    assert PHI_VAPOR_THRESHOLD <= rows[0]["phi"] < PHI_REALISED_THRESHOLD
    assert rows[0]["status"] == "partial"


def test_realisation_sweep_skips_when_no_metric_data(tmp_path: Path):
    """When BO.current AND snapshot are both None, the row stays pending."""
    p = tmp_path / "_promise_ledger.jsonl"
    promise_time = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
    sweep_time = promise_time + timedelta(days=10)
    append_promise(
        p, "TTO-A", {"BO-1": 0.40},
        bo_metrics_at_done={"BO-1": None, "BO-2": None},
        verified_done_at=promise_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        window_days=7,
    )
    # All BO.currents are None too
    bo1 = BO(id="BO-1", name="x", weight=30,
             metric="m", baseline=0.0, target=10.0, metric_source="manual",
             current=None)
    bo2 = BO(id="BO-2", name="y", weight=20)
    sprints = [Sprint(name="S", bos=[bo1, bo2])]
    result = run_realisation_sweep(p, sprints, now=sweep_time)
    assert result["skipped_no_data"] == 1
    assert result["updated"] == 0
    rows = read_all(p)
    assert rows[0]["status"] == "pending"  # untouched


def test_realisation_sweep_already_realised_rows_untouched(tmp_path: Path):
    """Idempotency: re-running the sweep doesn't re-process already-classified rows."""
    p = tmp_path / "_promise_ledger.jsonl"
    promise_time = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
    sweep_time = promise_time + timedelta(days=10)
    append_promise(
        p, "TTO-A", {"BO-1": 0.40},
        bo_metrics_at_done={"BO-1": 0.0, "BO-2": 0.0},
        verified_done_at=promise_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        window_days=7,
    )
    sprints = _sprints_for_sweep({"BO-1": 4.0})
    run_realisation_sweep(p, sprints, now=sweep_time)
    # second run should be a no-op
    result = run_realisation_sweep(p, sprints, now=sweep_time)
    assert result["checked"] == 0
    assert result["updated"] == 0
