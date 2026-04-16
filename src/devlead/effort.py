"""Effort tracking — record and aggregate tokens per TTO.

Ported from legacy/v1/src_devlead/effort.py. Adapted for v2's TTO IDs
instead of v1's TASK IDs. Mandatory per BO-001/TBO-003/TTO-024.

Appends effort entries to _effort_log.jsonl. Aggregates by TTO, TBO, and BO
for the dashboard's Token Economics tab.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def record_effort(
    docs_dir: Path,
    tto_id: str,
    tokens: int = 0,
    session_id: str = "",
) -> None:
    """Append an effort entry for a TTO."""
    entry = {
        "tto_id": tto_id,
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tokens": tokens,
        "session_id": session_id,
    }
    log = _log_path(docs_dir)
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=True) + "\n")


def get_tto_effort(docs_dir: Path, tto_id: str) -> dict:
    """Aggregate effort for a single TTO."""
    entries = [e for e in _read_log(docs_dir) if e.get("tto_id") == tto_id]
    return _aggregate(entries)


def get_tbo_effort(docs_dir: Path, tbo_id: str) -> dict:
    """Aggregate effort across all TTOs under a TBO. Requires hierarchy lookup."""
    from devlead import hierarchy
    h_path = docs_dir / "_project_hierarchy.md"
    if not h_path.exists():
        return _aggregate([])
    tto_ids = set()
    for s in hierarchy.parse(h_path):
        for bo in s.bos:
            for tbo in bo.tbos:
                if tbo.id == tbo_id:
                    tto_ids = {t.id for t in tbo.ttos}
    entries = [e for e in _read_log(docs_dir) if e.get("tto_id") in tto_ids]
    return _aggregate(entries)


def get_bo_effort(docs_dir: Path, bo_id: str) -> dict:
    """Aggregate effort across all TTOs under a BO."""
    from devlead import hierarchy
    h_path = docs_dir / "_project_hierarchy.md"
    if not h_path.exists():
        return _aggregate([])
    tto_ids = set()
    for s in hierarchy.parse(h_path):
        for bo in s.bos:
            if bo.id == bo_id:
                for tbo in bo.tbos:
                    tto_ids.update(t.id for t in tbo.ttos)
    entries = [e for e in _read_log(docs_dir) if e.get("tto_id") in tto_ids]
    return _aggregate(entries)


def get_all_effort(docs_dir: Path) -> dict[str, dict]:
    """Aggregate effort per TTO. Returns {tto_id: {total_tokens, sessions, first, last}}."""
    entries = _read_log(docs_dir)
    by_tto: dict[str, list[dict]] = {}
    for e in entries:
        tto_id = e.get("tto_id", "")
        if tto_id:
            by_tto.setdefault(tto_id, []).append(e)
    return {tto_id: _aggregate(elist) for tto_id, elist in by_tto.items()}


def summary(docs_dir: Path) -> str:
    """Plain-text effort summary."""
    all_effort = get_all_effort(docs_dir)
    if not all_effort:
        return "(no effort data recorded)"
    lines = ["Token effort by TTO:"]
    total = 0
    for tto_id in sorted(all_effort.keys()):
        e = all_effort[tto_id]
        lines.append(f"  {tto_id}: {e['total_tokens']:,} tokens ({e['sessions']} sessions)")
        total += e["total_tokens"]
    lines.append(f"  TOTAL: {total:,} tokens")
    return "\n".join(lines)


def _log_path(docs_dir: Path) -> Path:
    return Path(docs_dir) / "_effort_log.jsonl"


def _read_log(docs_dir: Path) -> list[dict]:
    log = _log_path(docs_dir)
    if not log.exists():
        return []
    entries = []
    for line in log.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def _aggregate(entries: list[dict]) -> dict:
    if not entries:
        return {"total_tokens": 0, "sessions": 0, "first": "", "last": ""}
    total = sum(e.get("tokens", 0) for e in entries)
    sessions = len({e.get("session_id", "") for e in entries} - {""})
    timestamps = sorted(e.get("ts", "") for e in entries if e.get("ts"))
    return {
        "total_tokens": total,
        "sessions": max(sessions, 1),
        "first": timestamps[0] if timestamps else "",
        "last": timestamps[-1] if timestamps else "",
    }
