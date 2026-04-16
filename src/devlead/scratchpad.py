"""Scratchpad helpers - read/append/iterate/convert entries in _scratchpad.md.

The scratchpad is a permanent raw-capture inbox. Entries are
`## Entry - <date> - <title>` blocks separated by `---` rules. Triage status
is tracked inside each entry body, not by this module.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ENTRY_HEADING_RE = re.compile(r"^## Entry - (\d{4}-\d{2}-\d{2}) - (.+?)\s*$", re.MULTILINE)


def read(scratchpad_path: Path) -> str:
    """Return the full text of _scratchpad.md."""
    return Path(scratchpad_path).read_text(encoding="utf-8")


def append_entry(
    scratchpad_path: Path,
    title: str,
    body: str,
    when: datetime | None = None,
) -> None:
    """Append a new ## heading entry with timestamp. `when` defaults to now(UTC)."""
    when = when or datetime.now(timezone.utc)
    date_str = when.strftime("%Y-%m-%d")
    title_clean = _sanitize_one_line(title)
    body_clean = body.rstrip() + "\n"

    block = f"\n## Entry - {date_str} - {title_clean}\n\n{body_clean}\n---\n"

    path = Path(scratchpad_path)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + block, encoding="utf-8")


def iter_untriaged(scratchpad_path: Path) -> list[tuple[str, str]]:
    """Return (entry_id, entry_title) tuples for every ## heading entry.

    `entry_id` is `<date>-<slug>` where slug is a lowercased, hyphen-joined
    title. v1 treats every entry as untriaged; triage state lives in the body.
    """
    text = read(scratchpad_path)
    results: list[tuple[str, str]] = []
    for match in ENTRY_HEADING_RE.finditer(text):
        date_str, title = match.group(1), match.group(2).strip()
        slug = _slugify(title)
        entry_id = f"{date_str}-{slug}" if slug else date_str
        results.append((entry_id, title))
    return results


def get_entry(scratchpad_path: Path, needle: str) -> tuple[str, str, str] | None:
    """Return (entry_id, title, body) for a matching scratchpad entry.

    `needle` is matched as a lowercased substring against both the entry_id
    and the title. Returns the first match in file order, or None if no match.
    """
    path = Path(scratchpad_path)
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    needle_lower = needle.lower()

    match_idx = -1
    target_entry_id = ""
    target_title = ""
    for i, line in enumerate(lines):
        m = ENTRY_HEADING_RE.match(line)
        if not m:
            continue
        date_str, title = m.group(1), m.group(2).strip()
        slug = _slugify(title)
        entry_id = f"{date_str}-{slug}" if slug else date_str
        if needle_lower in entry_id.lower() or needle_lower in title.lower():
            match_idx = i
            target_entry_id = entry_id
            target_title = title
            break

    if match_idx < 0:
        return None

    body_lines: list[str] = []
    i = match_idx + 1
    while i < len(lines):
        line = lines[i]
        if ENTRY_HEADING_RE.match(line):
            break
        if line.strip() == "---" and body_lines:
            break
        body_lines.append(line)
        i += 1

    return target_entry_id, target_title, "\n".join(body_lines).strip()


def append_cross_reference(
    scratchpad_path: Path, entry_needle: str, note: str
) -> bool:
    """Append a note line to an existing scratchpad entry's body.

    Returns True if the entry was found and updated, False otherwise.
    Used to cross-link scratchpad entries with their promoted intake entries.
    """
    path = Path(scratchpad_path)
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    needle_lower = entry_needle.lower()

    match_idx = -1
    for i, line in enumerate(lines):
        m = ENTRY_HEADING_RE.match(line)
        if not m:
            continue
        date_str, title = m.group(1), m.group(2).strip()
        slug = _slugify(title)
        entry_id = f"{date_str}-{slug}" if slug else date_str
        if needle_lower in entry_id.lower() or needle_lower in title.lower():
            match_idx = i
            break

    if match_idx < 0:
        return False

    end = match_idx + 1
    while end < len(lines):
        if ENTRY_HEADING_RE.match(lines[end]):
            break
        if lines[end].strip() == "---":
            break
        end += 1

    # Dedupe (L12 fix): skip if an identical note already exists in the body.
    note_stripped = note.strip()
    for existing_line in lines[match_idx + 1:end]:
        if existing_line.strip() == note_stripped:
            return True

    insert_at = end
    while insert_at > match_idx + 1 and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    lines.insert(insert_at, "")
    lines.insert(insert_at + 1, note)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def _iter_entry_blocks(text: str) -> list[tuple[str, str, str, str]]:
    """Split scratchpad text into entry blocks.

    Returns list of (entry_id, title, full_block, body) where full_block is the
    complete text from heading through trailing ``---`` separator (inclusive).
    """
    lines = text.splitlines(keepends=True)
    entries: list[tuple[str, str, str, str]] = []
    i = 0
    while i < len(lines):
        m = ENTRY_HEADING_RE.match(lines[i].rstrip("\n"))
        if not m:
            i += 1
            continue
        date_str, title = m.group(1), m.group(2).strip()
        slug = _slugify(title)
        entry_id = f"{date_str}-{slug}" if slug else date_str
        start = i
        i += 1
        # collect body lines until next heading or ---
        body_lines: list[str] = []
        while i < len(lines):
            if ENTRY_HEADING_RE.match(lines[i].rstrip("\n")):
                break
            if lines[i].rstrip("\n").strip() == "---":
                i += 1  # consume separator
                break
            body_lines.append(lines[i])
            i += 1
        full_block = "".join(lines[start:i])
        body = "".join(body_lines).strip()
        entries.append((entry_id, title, full_block, body))
    return entries


_PROMOTED_RE = re.compile(r"^>\s*\*\*(?:Promoted|Migrated):\*\*", re.MULTILINE)

# Matches intake IDs like FEATURES-0011, BUGS-0003, etc.
_INTAKE_ID_RE = re.compile(r"\b([A-Z]+-\d{4})\b")


def archive_promoted(
    scratchpad_path: Path,
    archive_path: Path | None = None,
) -> int:
    """Move promoted/migrated scratchpad entries to an archive file.

    An entry is archivable when its body contains a ``> **Promoted:**`` or
    ``> **Migrated:**`` line AND the referenced intake entry (if any) is NOT
    still ``in_progress``.

    Returns the count of entries archived.
    """
    from devlead import audit, intake  # local to avoid circular

    path = Path(scratchpad_path)
    if not path.exists():
        return 0

    if archive_path is None:
        archive_path = path.parent / "_scratchpad_archive.md"

    text = path.read_text(encoding="utf-8")
    blocks = _iter_entry_blocks(text)
    if not blocks:
        return 0

    docs_dir = path.parent
    archived: list[tuple[str, str, str]] = []  # (entry_id, title, full_block)

    for entry_id, title, full_block, body in blocks:
        if not _PROMOTED_RE.search(body):
            continue

        # Never archive entries whose promoted intake ID is still in_progress.
        intake_ids = _INTAKE_ID_RE.findall(body)
        skip = False
        for iid in intake_ids:
            found = intake.find_entry(docs_dir, iid)
            if found and found[0].status == "in_progress":
                skip = True
                break
        if skip:
            continue

        archived.append((entry_id, title, full_block))

    if not archived:
        return 0

    # Append archived entries to archive file.
    archive_text = archive_path.read_text(encoding="utf-8") if archive_path.exists() else ""
    if archive_text and not archive_text.endswith("\n"):
        archive_text += "\n"
    for entry_id, title, full_block in archived:
        archive_text += full_block
        if not full_block.endswith("\n"):
            archive_text += "\n"
    archive_path.write_text(archive_text, encoding="utf-8")

    # Remove archived entries from the source file.
    remaining = text
    for _, _, full_block in archived:
        remaining = remaining.replace(full_block, "", 1)
    # Collapse runs of 3+ blank lines down to 2.
    remaining = re.sub(r"\n{3,}", "\n\n", remaining)
    path.write_text(remaining, encoding="utf-8")

    # Audit each archival.
    for entry_id, title, _ in archived:
        audit.append_event(
            docs_dir,
            "scratchpad_archive",
            source=f"scratchpad:{entry_id}",
            message=f"archived entry: {title}",
        )

    return len(archived)


def _sanitize_one_line(text: str) -> str:
    return " ".join(text.split()).strip() or "untitled"


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python -m devlead.scratchpad <path-to-_scratchpad.md>")
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"not found: {path}")
        return 1
    entries = iter_untriaged(path)
    if not entries:
        print("(no entries)")
        return 0
    for entry_id, title in entries:
        print(f"{entry_id}\t{title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
