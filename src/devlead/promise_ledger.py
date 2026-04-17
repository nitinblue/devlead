"""Promise ledger — captures what each TTO promised vs what reality delivered.

When the verifier marks a TTO done, this module writes a promise row to
`devlead_docs/_promise_ledger.jsonl`. Each row is:

    {
      "tto_id": "TTO-1.4.1",
      "promised": {"BO-1": 0.40, "BO-3": 0.05},
      "verified_done_at": "2026-04-17T22:00:00Z",
      "bo_metrics_at_done": {"BO-1": 0.0, "BO-3": null, ...},
      "window_days": 7,
      "status": "pending",
      "realised": null,
      "phi": null,
      "epsilon": null
    }

After `verified_done_at + window_days`, a separate sweep computes the
realised vector from current BO metrics, calls `convergence.compute_phi`
and `compute_epsilon`, and updates the row's status to one of:
    realised | partial | missed | vapor | infrastructural

The realisation sweep lives in a future step; this module just writes the
pending rows. Tests live in tests/test_promise_ledger.py.

Part of FEATURES-0014. Schema specified in vision Tab 5.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

from devlead import convergence
from devlead.hierarchy import Sprint

DEFAULT_WINDOW_DAYS = 7

LEDGER_FILENAME = "_promise_ledger.jsonl"

# Realisation regime thresholds — tunable later via config.
PHI_REALISED_THRESHOLD = 0.80
PHI_VAPOR_THRESHOLD = 0.30


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_promise(
    ledger_path: Path,
    tto_id: str,
    promised: dict[str, float],
    bo_metrics_at_done: dict[str, float | None],
    *,
    verified_done_at: str | None = None,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> dict:
    """Append a single promise row to the ledger. Returns the row written."""
    row = {
        "tto_id": tto_id,
        "promised": promised,
        "verified_done_at": verified_done_at or _now_iso(),
        "bo_metrics_at_done": bo_metrics_at_done,
        "window_days": window_days,
        "status": "pending",
        "realised": None,
        "phi": None,
        "epsilon": None,
    }
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


def read_all(ledger_path: Path) -> list[dict]:
    """Read every row from the ledger. Returns [] if the file is missing.

    Malformed rows are silently skipped — partial reads are better than crashing
    the dashboard on one bad line.
    """
    p = Path(ledger_path)
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


def collect_bo_metrics(sprints: list[Sprint]) -> dict[str, float | None]:
    """Snapshot every BO's `current` metric value into a dict.

    None for BOs that haven't declared a metric_source or have no current reading.
    """
    out: dict[str, float | None] = {}
    for s in sprints:
        for bo in s.bos:
            out[bo.id] = bo.current
    return out


def write_promises_for(
    ledger_path: Path,
    sprints: list[Sprint],
    tto_ids: Iterable[str],
    *,
    verified_done_at: str | None = None,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> list[dict]:
    """Write a promise row for each TTO ID in `tto_ids`.

    Skips TTOs whose intent_vector is empty (no quantified promise to evaluate
    later — counts as "infrastructural" work). Returns the rows written.
    """
    metrics_snapshot = collect_bo_metrics(sprints)
    tto_index = {
        tto.id: tto
        for s in sprints for bo in s.bos
        for tbo in bo.tbos for tto in tbo.ttos
    }
    written: list[dict] = []
    for tid in tto_ids:
        tto = tto_index.get(tid)
        if tto is None or not tto.intent_vector:
            continue
        row = append_promise(
            ledger_path=ledger_path,
            tto_id=tid,
            promised=dict(tto.intent_vector),
            bo_metrics_at_done=dict(metrics_snapshot),
            verified_done_at=verified_done_at,
            window_days=window_days,
        )
        written.append(row)
    return written


# --- realisation sweep ----------------------------------------------------


def _bo_index_from(sprints: list[Sprint]) -> dict[str, "BO"]:  # type: ignore[name-defined]
    """Flat lookup of {bo_id: BO} across all sprints."""
    return {bo.id: bo for s in sprints for bo in s.bos}


def _normalise_change(bo, value_now: float | None, value_at_done: float | None) -> float:
    """Convert raw metric change into normalised-axis units (matches intent_vector).

    Returns 0.0 when any required field is missing — silent degradation, no crash.
    """
    if value_now is None or value_at_done is None:
        return 0.0
    if bo.baseline is None or bo.target is None:
        return 0.0
    denom = bo.target - bo.baseline
    if denom == 0.0:
        return 0.0
    return (value_now - value_at_done) / denom


def _vector_from_dict(d: dict, bo_order: list[str]) -> tuple[float, ...]:
    """Build a fixed-order vector from a {bo_id: value} dict."""
    return tuple(float(d.get(bo_id, 0.0) or 0.0) for bo_id in bo_order)


def _classify(phi: float) -> str:
    """Map φ to a regime label (used only for status field; ε also reported)."""
    if phi >= PHI_REALISED_THRESHOLD:
        return "realised"
    if phi < PHI_VAPOR_THRESHOLD:
        return "vapor"
    return "partial"


def _is_window_expired(row: dict, now: datetime) -> bool:
    """True if verified_done_at + window_days <= now."""
    ts = row.get("verified_done_at")
    if not ts:
        return False
    try:
        # Tolerate trailing Z
        done = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return False
    window = timedelta(days=int(row.get("window_days", DEFAULT_WINDOW_DAYS)))
    return done + window <= now


def run_realisation_sweep(
    ledger_path: Path,
    sprints: list[Sprint],
    *,
    now: datetime | None = None,
) -> dict:
    """Update every pending row whose window has expired.

    For each such row:
      - reads each BO's current value (must come from caller — typically applied
        via metric_source.apply_to_sprints before this call)
      - computes per-axis normalised realisation
      - calls convergence.compute_phi and compute_epsilon
      - writes status, realised, phi, epsilon back to the row

    Returns: {"checked": N, "updated": M, "skipped_no_data": K}.
    Rewrites the ledger file if any rows updated. Append-only invariant
    relaxed for status updates — documented trade-off.
    """
    rows = read_all(ledger_path)
    if not rows:
        return {"checked": 0, "updated": 0, "skipped_no_data": 0}

    now = now or datetime.now(timezone.utc)
    bo_index = _bo_index_from(sprints)
    # Stable BO ordering for vector math: by id alphabetical
    bo_order = sorted(bo_index.keys())
    weights = [bo_index[bid].weight for bid in bo_order]
    total_w = sum(weights) or 1
    g = tuple(w / total_w for w in weights)  # normalised weights, sum = 1

    checked = 0
    updated = 0
    skipped = 0

    for row in rows:
        if row.get("status") != "pending":
            continue
        if not _is_window_expired(row, now):
            continue
        checked += 1

        promised_vec = _vector_from_dict(row.get("promised", {}), bo_order)
        snapshot = row.get("bo_metrics_at_done", {})
        realised_components = []
        any_data = False
        for bid in bo_order:
            bo = bo_index.get(bid)
            if bo is None:
                realised_components.append(0.0)
                continue
            normalised = _normalise_change(bo, bo.current, snapshot.get(bid))
            realised_components.append(normalised)
            if bo.current is not None and snapshot.get(bid) is not None:
                any_data = True
        if not any_data:
            skipped += 1
            continue

        realised_vec = tuple(realised_components)
        phi = convergence.compute_phi(realised_vec, promised_vec)
        eps = convergence.compute_epsilon(realised_vec, promised_vec, g)

        row["realised"] = {bid: realised_components[i] for i, bid in enumerate(bo_order)
                            if realised_components[i] != 0.0}
        row["phi"] = phi
        row["epsilon"] = eps
        row["status"] = _classify(phi)
        row["realised_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        updated += 1

    if updated > 0:
        with open(ledger_path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    return {"checked": checked, "updated": updated, "skipped_no_data": skipped}
