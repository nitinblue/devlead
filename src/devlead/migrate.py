"""DevLead content migration. Implements FEATURES-0006.

Hash-checked, reversible content migration between devlead_docs/ files with
zero-loss guarantee. Always strict -- information loss is unrecoverable.

Migrations are logged to `devlead_docs/_migration_log.jsonl`. Every migration
can be rolled back by ID.

ASCII only. Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

_LOG_NAME = "_migration_log.jsonl"


@dataclass
class MigrationRecord:
    id: str
    ts: str
    source: str
    dest: str
    section_heading: str
    content_hash: str
    status: str  # applied | rolled_back

    # Position in source file (line index, 0-based) for rollback re-insertion.
    source_position: int = 0
    # The migrated content itself (needed for rollback).
    content: str = ""


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short_uuid() -> str:
    return uuid.uuid4().hex[:12]


def _content_hash(text: str) -> str:
    stripped = re.sub(r"\s+", "", text)
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()


def _extract_section(text: str, heading: str) -> tuple[str, int, int] | None:
    """Find a ## section by heading. Returns (content, start_line, end_line).

    Content includes the heading line itself. end_line is exclusive.
    """
    lines = text.splitlines(keepends=True)
    pattern = re.compile(r"^##\s+" + re.escape(heading) + r"\s*$")
    start: int | None = None
    for i, line in enumerate(lines):
        if pattern.match(line.rstrip("\n\r")):
            start = i
            continue
        if start is not None and re.match(r"^##\s+", line):
            return "".join(lines[start:i]), start, i
    if start is not None:
        return "".join(lines[start:]), start, len(lines)
    return None


def _append_log(docs_dir: Path, record: MigrationRecord) -> None:
    log_path = docs_dir / _LOG_NAME
    line = json.dumps(asdict(record), ensure_ascii=True, sort_keys=False)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _update_log_status(docs_dir: Path, migration_id: str, new_status: str) -> None:
    """Rewrite the JSONL log, flipping status for the given ID."""
    log_path = docs_dir / _LOG_NAME
    if not log_path.exists():
        return
    lines = log_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            out.append(line)
            continue
        if rec.get("id") == migration_id:
            rec["status"] = new_status
            out.append(json.dumps(rec, ensure_ascii=True, sort_keys=False))
        else:
            out.append(line)
    log_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def migrate(
    source_path: Path,
    section_heading: str,
    dest_path: Path,
    docs_dir: Path,
) -> MigrationRecord:
    """Migrate a section from source to dest with hash verification.

    The destination file must already contain the section content (copy-first
    pattern). Raises ValueError if hash mismatch or section not found.
    """
    from devlead import audit

    source_path = Path(source_path)
    dest_path = Path(dest_path)
    docs_dir = Path(docs_dir)

    if not source_path.exists():
        raise ValueError(f"source not found: {source_path}")
    if not dest_path.exists():
        raise ValueError(f"dest not found: {dest_path}")

    source_text = source_path.read_text(encoding="utf-8")
    extracted = _extract_section(source_text, section_heading)
    if extracted is None:
        raise ValueError(
            f"section '## {section_heading}' not found in {source_path}"
        )
    section_content, start_line, end_line = extracted
    src_hash = _content_hash(section_content)

    # Verify destination contains matching content.
    dest_text = dest_path.read_text(encoding="utf-8")
    dest_hash = _content_hash(
        _find_section_in_dest(dest_text, section_heading, section_content)
    )
    if src_hash != dest_hash:
        raise ValueError(
            f"hash mismatch: destination does not contain matching content "
            f"for '## {section_heading}' (source={src_hash[:16]}.. "
            f"dest={dest_hash[:16]}..)"
        )

    # Remove section from source.
    lines = source_text.splitlines(keepends=True)
    new_source = "".join(lines[:start_line] + lines[end_line:])
    source_path.write_text(new_source, encoding="utf-8")

    record = MigrationRecord(
        id=_short_uuid(),
        ts=_utc_now(),
        source=str(source_path),
        dest=str(dest_path),
        section_heading=section_heading,
        content_hash=src_hash,
        status="applied",
        source_position=start_line,
        content=section_content,
    )
    _append_log(docs_dir, record)
    audit.append_event(
        docs_dir,
        "migrate",
        source=str(source_path),
        dest=str(dest_path),
        section=section_heading,
        migration_id=record.id,
        result="applied",
    )
    return record


def _find_section_in_dest(dest_text: str, heading: str, fallback_content: str) -> str:
    """Locate the section in dest. If exact heading match exists, return it.
    Otherwise return fallback_content for hash comparison (will fail)."""
    result = _extract_section(dest_text, heading)
    if result is not None:
        return result[0]
    # Heading not found as a section -- check if the raw content appears.
    stripped_fallback = re.sub(r"\s+", "", fallback_content)
    stripped_dest = re.sub(r"\s+", "", dest_text)
    if stripped_fallback in stripped_dest:
        return fallback_content
    return ""  # Will cause hash mismatch.


def rollback(migration_id: str, docs_dir: Path) -> str:
    """Roll back a migration by ID. Returns a summary string."""
    from devlead import audit

    docs_dir = Path(docs_dir)
    log_path = docs_dir / _LOG_NAME
    if not log_path.exists():
        raise ValueError("no migration log found")

    record: MigrationRecord | None = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if data.get("id") == migration_id:
            record = MigrationRecord(**{
                k: data[k]
                for k in MigrationRecord.__dataclass_fields__
                if k in data
            })
            break

    if record is None:
        raise ValueError(f"migration {migration_id} not found in log")
    if record.status == "rolled_back":
        raise ValueError(f"migration {migration_id} already rolled back")
    if not record.content:
        raise ValueError(
            f"migration {migration_id} has no stored content; cannot rollback"
        )

    source_path = Path(record.source)
    if not source_path.exists():
        raise ValueError(f"source file missing: {source_path}")

    # Re-insert content at original position (or end if file is shorter).
    source_text = source_path.read_text(encoding="utf-8")
    lines = source_text.splitlines(keepends=True)
    insert_at = min(record.source_position, len(lines))
    content_lines = record.content.splitlines(keepends=True)
    new_lines = lines[:insert_at] + content_lines + lines[insert_at:]
    source_path.write_text("".join(new_lines), encoding="utf-8")

    _update_log_status(docs_dir, migration_id, "rolled_back")
    audit.append_event(
        docs_dir,
        "migrate_rollback",
        migration_id=migration_id,
        source=record.source,
        section=record.section_heading,
        result="rolled_back",
    )
    return f"rolled back {migration_id}: re-inserted '## {record.section_heading}' into {record.source}"


def list_migrations(docs_dir: Path) -> list[MigrationRecord]:
    """Read all migration records from the JSONL log."""
    docs_dir = Path(docs_dir)
    log_path = docs_dir / _LOG_NAME
    if not log_path.exists():
        return []
    out: list[MigrationRecord] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            out.append(MigrationRecord(**{
                k: data[k]
                for k in MigrationRecord.__dataclass_fields__
                if k in data
            }))
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
    return out
