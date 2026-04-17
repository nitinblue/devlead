"""Tests for src/devlead/metric_source.py.

Part of FEATURES-0014 Step 6 — manual metric_source adapter.
"""
from __future__ import annotations

import json
from pathlib import Path

from devlead.metric_source import (
    HISTORY_FILENAME,
    latest_values,
    read_history,
    read_latest,
    record_reading,
)


def test_record_reading_writes_one_row(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    row = record_reading(p, "BO-1", 12.0)
    assert row["bo_id"] == "BO-1"
    assert row["value"] == 12.0
    assert row["source"] == "manual"
    assert "ts" in row
    assert p.exists()


def test_record_reading_appends_not_overwrites(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    record_reading(p, "BO-1", 5.0, ts="2026-04-17T10:00:00Z")
    record_reading(p, "BO-1", 8.0, ts="2026-04-17T11:00:00Z")
    rows = read_history(p)
    assert len(rows) == 2
    assert rows[0]["value"] == 5.0
    assert rows[1]["value"] == 8.0


def test_record_reading_creates_parent_dir(tmp_path: Path):
    p = tmp_path / "nested" / "subdir" / "_state_history.jsonl"
    record_reading(p, "BO-1", 1.0)
    assert p.exists()


def test_record_reading_coerces_int_to_float(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    row = record_reading(p, "BO-1", 5)
    assert isinstance(row["value"], float)
    assert row["value"] == 5.0


def test_record_reading_explicit_timestamp(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    row = record_reading(p, "BO-1", 1.0, ts="2026-01-01T00:00:00Z")
    assert row["ts"] == "2026-01-01T00:00:00Z"


def test_record_reading_with_note(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    row = record_reading(p, "BO-1", 1.0, note="post-launch reading")
    assert row["note"] == "post-launch reading"


def test_read_history_empty_when_no_file(tmp_path: Path):
    assert read_history(tmp_path / "nope.jsonl") == []


def test_read_history_skips_malformed(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    p.write_text(
        '{"bo_id": "BO-1", "value": 1.0}\n'
        'garbage\n'
        '\n'
        '{"bo_id": "BO-2", "value": 2.0}\n',
        encoding="utf-8",
    )
    rows = read_history(p)
    assert [r["bo_id"] for r in rows] == ["BO-1", "BO-2"]


def test_read_latest_returns_most_recent_per_bo(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    record_reading(p, "BO-1", 5.0, ts="2026-04-17T10:00:00Z")
    record_reading(p, "BO-1", 8.0, ts="2026-04-17T11:00:00Z")
    record_reading(p, "BO-1", 6.0, ts="2026-04-17T09:00:00Z")  # older, ignored
    record_reading(p, "BO-2", 100.0, ts="2026-04-17T11:00:00Z")
    latest = read_latest(p, "BO-1")
    assert latest is not None
    assert latest["value"] == 8.0
    assert latest["ts"] == "2026-04-17T11:00:00Z"


def test_read_latest_returns_none_for_unknown_bo(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    record_reading(p, "BO-1", 1.0)
    assert read_latest(p, "BO-99") is None


def test_read_latest_empty_file(tmp_path: Path):
    assert read_latest(tmp_path / "nope.jsonl", "BO-1") is None


def test_latest_values_aggregates_across_bos(tmp_path: Path):
    p = tmp_path / "_state_history.jsonl"
    record_reading(p, "BO-1", 5.0, ts="2026-04-17T10:00:00Z")
    record_reading(p, "BO-1", 8.0, ts="2026-04-17T11:00:00Z")  # newer
    record_reading(p, "BO-2", 50.0, ts="2026-04-17T10:00:00Z")
    record_reading(p, "BO-3", 1.0, ts="2026-04-17T10:00:00Z")
    vals = latest_values(p)
    assert vals == {"BO-1": 8.0, "BO-2": 50.0, "BO-3": 1.0}


def test_latest_values_empty_when_no_history(tmp_path: Path):
    assert latest_values(tmp_path / "nope.jsonl") == {}


def test_history_filename_constant():
    """The constant must match the path used in cli.py to avoid divergence."""
    assert HISTORY_FILENAME == "_state_history.jsonl"


# --- apply_to_sprints (history overlay onto BO.current) -------------------

def test_apply_to_sprints_overrides_current(tmp_path: Path):
    from devlead.hierarchy import BO, Sprint
    from devlead.metric_source import apply_to_sprints
    p = tmp_path / "_state_history.jsonl"
    record_reading(p, "BO-1", 12.0, ts="2026-04-17T11:00:00Z")
    record_reading(p, "BO-2", 0.5, ts="2026-04-17T11:00:00Z")
    bo1 = BO(id="BO-1", name="x", weight=30, current=None)
    bo2 = BO(id="BO-2", name="y", weight=30, current=0.0)  # MD value, will be overridden
    bo3 = BO(id="BO-3", name="z", weight=30, current=99.0)  # no history -> preserved
    sprints = [Sprint(name="S", bos=[bo1, bo2, bo3])]
    n = apply_to_sprints(p, sprints)
    assert n == 2
    assert bo1.current == 12.0
    assert bo2.current == 0.5
    assert bo3.current == 99.0


def test_apply_to_sprints_no_history_no_change(tmp_path: Path):
    from devlead.hierarchy import BO, Sprint
    from devlead.metric_source import apply_to_sprints
    bo = BO(id="BO-1", name="x", weight=30, current=42.0)
    sprints = [Sprint(name="S", bos=[bo])]
    n = apply_to_sprints(tmp_path / "nope.jsonl", sprints)
    assert n == 0
    assert bo.current == 42.0
