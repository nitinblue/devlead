# src/devlead/audit.py
"""Audit layer — log every file write with session context.

Parses Claude Code hook stdin JSON, extracts file_path + metadata,
appends to _audit_log.jsonl in devlead_docs/.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class AuditEntry:
    """A single audit log entry."""

    session_id: str = ""
    cwd: str = ""
    tool_name: str = ""
    file_path: str | None = None
    state: str = ""
    agent_id: str | None = None
    agent_type: str | None = None
    token_count: int = 0
    model_name: str = ""


def parse_hook_stdin(stdin_text: str) -> AuditEntry | None:
    """Parse Claude Code hook stdin JSON into an AuditEntry.

    Returns None if JSON is malformed.
    """
    try:
        data = json.loads(stdin_text)
    except (json.JSONDecodeError, TypeError):
        return None

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path")

    # Extract token count: check "token_count" directly, or nested "usage"
    token_count = data.get("token_count", 0)
    if not token_count:
        usage = data.get("usage", {})
        if isinstance(usage, dict):
            token_count = usage.get("total_tokens", 0) or (
                usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
            )
    token_count = int(token_count) if token_count else 0

    model_name = data.get("model_name", "") or data.get("model", "")

    return AuditEntry(
        session_id=data.get("session_id", ""),
        cwd=data.get("cwd", ""),
        tool_name=data.get("tool_name", ""),
        file_path=file_path,
        agent_id=data.get("agent_id"),
        agent_type=data.get("agent_type"),
        token_count=token_count,
        model_name=model_name,
    )


def log_write(entry: AuditEntry, log_file: Path) -> None:
    """Append an audit entry to the JSONL log file.

    Adds timestamp and cross_project flag automatically.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Detect cross-project write
    cross_project = False
    if entry.file_path and entry.cwd:
        try:
            file_resolved = str(Path(entry.file_path).resolve())
            cwd_resolved = str(Path(entry.cwd).resolve())
            cross_project = not file_resolved.startswith(cwd_resolved)
        except (ValueError, OSError):
            cross_project = False

    record = {
        "timestamp": now,
        "session_id": entry.session_id,
        "cwd": entry.cwd,
        "tool_name": entry.tool_name,
        "file_path": entry.file_path,
        "state": entry.state,
        "agent_id": entry.agent_id,
        "agent_type": entry.agent_type,
        "cross_project": cross_project,
        "token_count": entry.token_count,
        "model_name": entry.model_name,
    }

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_audit_log(log_file: Path) -> list[dict]:
    """Read all entries from the audit log."""
    if not log_file.exists():
        return []
    entries = []
    for line in log_file.read_text().strip().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries
