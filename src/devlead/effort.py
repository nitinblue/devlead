# src/devlead/effort.py
"""Effort tracking — record and aggregate token/time per task.

Appends effort entries to _effort_log.jsonl, aggregates by task and story.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from devlead.doc_parser import parse_table


def _load_session_id(docs_dir: Path) -> str:
    """Read session_id from session_state.json if it exists."""
    state_file = docs_dir / "session_state.json"
    if not state_file.exists():
        return ""
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        return data.get("session_id", "")
    except (json.JSONDecodeError, OSError):
        return ""


def _effort_log_path(docs_dir: Path) -> Path:
    return docs_dir / "_effort_log.jsonl"


def record_task_effort(
    docs_dir: Path,
    task_id: str,
    tokens: int = 0,
    session_id: str = "",
) -> None:
    """Append an effort entry for a task.

    Args:
        docs_dir: Path to claude_docs directory.
        task_id: The task ID (e.g. TASK-045).
        tokens: Token count for this entry.
        session_id: Override session ID; if empty, read from state file.
    """
    if not session_id:
        session_id = _load_session_id(docs_dir)

    entry = {
        "task_id": task_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tokens": tokens,
        "session_id": session_id,
    }

    log_file = _effort_log_path(docs_dir)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _read_effort_log(docs_dir: Path) -> list[dict]:
    """Read all entries from the effort log."""
    log_file = _effort_log_path(docs_dir)
    if not log_file.exists():
        return []
    entries = []
    for line in log_file.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def get_task_effort(docs_dir: Path, task_id: str) -> dict:
    """Aggregate effort for a single task.

    Returns:
        total_tokens: sum of all token entries
        session_count: number of unique sessions
        first_seen: earliest timestamp (ISO string or "")
        last_seen: latest timestamp (ISO string or "")
        duration_estimate: last_seen - first_seen in seconds (0 if < 2 entries)
    """
    entries = _read_effort_log(docs_dir)
    task_entries = [e for e in entries if e.get("task_id") == task_id]

    if not task_entries:
        return {
            "total_tokens": 0,
            "session_count": 0,
            "first_seen": "",
            "last_seen": "",
            "duration_estimate": 0,
        }

    total_tokens = sum(e.get("tokens", 0) for e in task_entries)
    sessions = {e.get("session_id", "") for e in task_entries}
    sessions.discard("")
    timestamps = sorted(e.get("timestamp", "") for e in task_entries if e.get("timestamp"))

    first_seen = timestamps[0] if timestamps else ""
    last_seen = timestamps[-1] if timestamps else ""

    duration = 0
    if len(timestamps) >= 2:
        try:
            t0 = datetime.fromisoformat(first_seen)
            t1 = datetime.fromisoformat(last_seen)
            duration = int((t1 - t0).total_seconds())
        except (ValueError, TypeError):
            duration = 0

    return {
        "total_tokens": total_tokens,
        "session_count": len(sessions),
        "first_seen": first_seen,
        "last_seen": last_seen,
        "duration_estimate": duration,
    }


def _get_task_story_map(docs_dir: Path) -> dict[str, str]:
    """Build task_id -> story_id mapping from _project_tasks.md."""
    tasks_file = docs_dir / "_project_tasks.md"
    if not tasks_file.exists():
        return {}
    text = tasks_file.read_text(encoding="utf-8")
    rows = parse_table(text)
    mapping = {}
    for row in rows:
        tid = row.get("ID", "").strip()
        sid = row.get("Story", "").strip()
        if tid and sid and sid != "\u2014":
            mapping[tid] = sid
    return mapping


def get_story_effort(docs_dir: Path, story_id: str) -> dict:
    """Aggregate effort across all tasks belonging to a story.

    Returns:
        total_tokens: sum across child tasks
        session_count: unique sessions across child tasks
        task_count: number of child tasks with effort data
    """
    task_story = _get_task_story_map(docs_dir)
    child_tasks = [tid for tid, sid in task_story.items() if sid == story_id]

    if not child_tasks:
        return {"total_tokens": 0, "session_count": 0, "task_count": 0}

    entries = _read_effort_log(docs_dir)
    child_set = set(child_tasks)
    relevant = [e for e in entries if e.get("task_id") in child_set]

    total_tokens = sum(e.get("tokens", 0) for e in relevant)
    sessions = {e.get("session_id", "") for e in relevant}
    sessions.discard("")
    tasks_with_effort = {e.get("task_id") for e in relevant}

    return {
        "total_tokens": total_tokens,
        "session_count": len(sessions),
        "task_count": len(tasks_with_effort),
    }
