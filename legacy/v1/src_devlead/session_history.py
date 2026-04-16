"""Session history — capture snapshots for trend tracking.

Appends one JSONL line per session with all metrics.
Enables day-over-day delta computation and drift detection.
"""

import json
from datetime import date
from pathlib import Path

from devlead.doc_parser import get_builtin_vars


def capture_session_snapshot(
    docs_dir: Path,
    state: dict,
    history_file: Path,
    today: date | None = None,
) -> None:
    """Capture a snapshot of all metrics and append to history.

    Called at session end (transition to SESSION_END or UPDATE).
    """
    if today is None:
        today = date.today()

    vars = get_builtin_vars(docs_dir, today=today)
    transitions = state.get("transitions", [])

    record = {
        "date": today.isoformat(),
        "state": state.get("state", ""),
        "transitions": len(transitions),
        # All builtin vars captured
        **vars,
    }

    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_session_history(history_file: Path) -> list[dict]:
    """Read all session snapshots from history file."""
    if not history_file.exists():
        return []
    entries = []
    for line in history_file.read_text().strip().splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def compute_deltas(history: list[dict]) -> dict[str, float]:
    """Compute deltas between the last two sessions.

    Returns dict of {metric: change}. Positive = increased, negative = decreased.
    Only numeric fields are compared. Returns empty dict if less than 2 sessions.
    """
    if len(history) < 2:
        return {}

    prev = history[-2]
    curr = history[-1]

    deltas = {}
    for key in curr:
        if key in prev:
            curr_val = curr[key]
            prev_val = prev[key]
            if isinstance(curr_val, (int, float)) and isinstance(prev_val, (int, float)):
                deltas[key] = curr_val - prev_val

    return deltas
