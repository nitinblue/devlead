"""DevLead audit log writer. Implements FEATURES-0010.

Append-only JSONL log at `devlead_docs/_audit_log.jsonl`. Every command writes
one event. Schema per HTML section 8.1 of
docs/memory_and_enforcement_design_2026-04-14.html:

    {ts, event, tool?, cwi?, intake_id?, source?, origin?, result?,
     message?, file?, rule?}

`ts` and `event` are added automatically; the caller passes the rest as kwargs.

Audit MUST NOT break the caller. All write failures are logged to stderr and
swallowed. If the parent directory is missing the file is simply not written.

ASCII only. Stdlib only.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_LOG_NAME = "_audit_log.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_event(docs_dir: Path, event: str, **fields) -> None:
    """Append one JSON line to `<docs_dir>/_audit_log.jsonl`. Never raises."""
    try:
        docs_dir = Path(docs_dir)
        if not docs_dir.exists():
            return
        record: dict = {"ts": _utc_now(), "event": event}
        for k, v in fields.items():
            if v is None:
                continue
            record[k] = v
        line = json.dumps(record, ensure_ascii=True, sort_keys=False)
        log_path = docs_dir / _LOG_NAME
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception as e:  # noqa: BLE001 - audit must never break the caller
        print(f"devlead: audit write failed: {e}", file=sys.stderr)


def tail(docs_dir: Path, n: int = 20) -> list[dict]:
    """Return the last `n` audit events as dicts (oldest first). Never raises."""
    try:
        log_path = Path(docs_dir) / _LOG_NAME
        if not log_path.exists():
            return []
        lines = log_path.read_text(encoding="utf-8").splitlines()
        out: list[dict] = []
        for line in lines[-n:]:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out
    except Exception as e:  # noqa: BLE001
        print(f"devlead: audit tail failed: {e}", file=sys.stderr)
        return []
