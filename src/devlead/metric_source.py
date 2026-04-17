"""Metric source adapter — manual mode for v1.

Stores a durable history of BO metric readings in `_state_history.jsonl`,
one append-only row per reading:

    {
      "ts": "2026-04-17T22:00:00Z",
      "bo_id": "BO-1",
      "value": 12.0,
      "source": "manual",
      "note": ""
    }

Convergence math (`convergence.compute_C`) reads the latest reading per BO
from this history if present, falling back to the `current:` field declared
in `_project_hierarchy.md`. The MD field is the documented intent; the
history is the runtime record.

Modes (only `manual` shipped in v1):
  - manual          → user runs `devlead metric-update <BO-ID> <value>`
  - shell:<cmd>     → DEFERRED: Stop hook runs cmd, parses stdout
  - url:<endpoint>  → DEFERRED: Stop hook GETs endpoint, extracts JSON path

Part of FEATURES-0014 Step 6.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_FILENAME = "_state_history.jsonl"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_reading(
    history_path: Path,
    bo_id: str,
    value: float,
    *,
    source: str = "manual",
    note: str = "",
    ts: str | None = None,
) -> dict:
    """Append a single metric reading to the history file. Returns the row."""
    row = {
        "ts": ts or _now_iso(),
        "bo_id": bo_id,
        "value": float(value),
        "source": source,
        "note": note,
    }
    history_path = Path(history_path)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


def read_history(history_path: Path) -> list[dict]:
    """Read every row from the history. Returns [] if missing.

    Malformed rows skipped silently.
    """
    p = Path(history_path)
    if not p.exists():
        return []
    rows: list[dict] = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def read_latest(history_path: Path, bo_id: str) -> dict | None:
    """Return the most recent reading for `bo_id`, or None if no history."""
    latest: dict | None = None
    for row in read_history(history_path):
        if row.get("bo_id") != bo_id:
            continue
        if latest is None or row.get("ts", "") > latest.get("ts", ""):
            latest = row
    return latest


def latest_values(history_path: Path) -> dict[str, float]:
    """Return {bo_id: latest_value} across all BOs with at least one reading."""
    out: dict[str, float] = {}
    out_ts: dict[str, str] = {}
    for row in read_history(history_path):
        bo_id = row.get("bo_id")
        ts = row.get("ts", "")
        if not bo_id or "value" not in row:
            continue
        if bo_id not in out_ts or ts > out_ts[bo_id]:
            out[bo_id] = float(row["value"])
            out_ts[bo_id] = ts
    return out


def apply_to_sprints(history_path: Path, sprints: list) -> int:
    """Override BO.current on every BO that has a reading in history.

    Returns the number of BOs whose `current` was updated. The MD-declared
    `current:` (if any) is preserved when no history exists for that BO.
    """
    latest = latest_values(history_path)
    updated = 0
    for s in sprints:
        for bo in s.bos:
            if bo.id in latest:
                bo.current = latest[bo.id]
                updated += 1
    return updated
