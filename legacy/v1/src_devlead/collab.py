"""Cross-project collaboration channel — .collab/ INBOX/OUTBOX."""

import re
import shutil
from datetime import date
from pathlib import Path


def init_collab(project_dir: Path) -> None:
    """Create .collab/INBOX/ and .collab/OUTBOX/ directories."""
    collab = project_dir / ".collab"
    (collab / "INBOX").mkdir(parents=True, exist_ok=True)
    (collab / "OUTBOX").mkdir(parents=True, exist_ok=True)


def scan_inbox(project_dir: Path) -> list[dict]:
    """Scan .collab/INBOX/ for request/feedback files.

    Returns list of dicts with filename and parsed metadata.
    """
    inbox = project_dir / ".collab" / "INBOX"
    if not inbox.exists():
        return []

    items = []
    for f in sorted(inbox.glob("*.md")):
        content = f.read_text()
        meta = parse_collab_file(content)
        meta["filename"] = f.name
        items.append(meta)

    return items


def parse_collab_file(content: str) -> dict:
    """Parse a collab file and extract metadata.

    Expected format:
        # REQUEST: Title here
        > From: project_name
        > To: project_name
        > Date: 2026-04-05
        > Priority: P1
        > Status: OPEN
    """
    meta: dict[str, str] = {
        "type": "",
        "title": "",
        "from": "",
        "to": "",
        "date": "",
        "priority": "",
        "status": "",
    }

    lines = content.splitlines()

    # Parse title line
    for line in lines:
        m = re.match(r"^#\s+(REQUEST|FEEDBACK|CHANGE_REQUEST|ISSUE_ESCALATION|STATUS_UPDATE):\s*(.+)", line)
        if m:
            meta["type"] = m.group(1)
            meta["title"] = m.group(2).strip()
            break

    # Parse metadata lines
    for line in lines:
        m = re.match(r"^>\s*(\w+):\s*(.+)", line)
        if m:
            key = m.group(1).lower()
            value = m.group(2).strip()
            if key in meta:
                meta[key] = value

    return meta


def collab_status(project_dir: Path) -> dict:
    """Get collab status summary."""
    inbox = project_dir / ".collab" / "INBOX"
    outbox = project_dir / ".collab" / "OUTBOX"

    inbox_count = len(list(inbox.glob("*.md"))) if inbox.exists() else 0
    outbox_count = len(list(outbox.glob("*.md"))) if outbox.exists() else 0

    inbox_items = scan_inbox(project_dir)
    open_requests = [i for i in inbox_items if i.get("status", "").upper() == "OPEN"]

    return {
        "inbox_count": inbox_count,
        "outbox_count": outbox_count,
        "open_requests": len(open_requests),
    }


def _next_sequence(outbox: Path, prefix: str) -> int:
    """Find next sequence number for a given prefix in outbox."""
    existing = list(outbox.glob(f"{prefix}_*.md"))
    if not existing:
        return 1
    nums = []
    for f in existing:
        parts = f.stem.rsplit("_", 1)
        if parts[-1].isdigit():
            nums.append(int(parts[-1]))
    return max(nums, default=0) + 1


def _create_collab_message(
    project_dir: Path,
    msg_type: str,
    to_project: str,
    title: str,
    body: str,
    priority: str = "",
    blocks: str = "",
    references: str = "",
) -> Path:
    """Create a structured collab message in OUTBOX."""
    outbox = project_dir / ".collab" / "OUTBOX"
    outbox.mkdir(parents=True, exist_ok=True)

    prefix = f"{msg_type}_{to_project}"
    seq = _next_sequence(outbox, prefix)
    filename = f"{prefix}_{seq:03d}.md"
    filepath = outbox / filename

    today = str(date.today())
    from_project = project_dir.name

    lines = [
        f"# {msg_type}: {title}",
        "",
        f"> From: {from_project}",
        f"> To: {to_project}",
        f"> Date: {today}",
    ]
    if priority:
        lines.append(f"> Priority: {priority}")
    lines.append("> Status: OPEN")
    if blocks:
        lines.append(f"> Blocks: {blocks}")
    if references:
        lines.append(f"> References: {references}")
    lines.extend(["", "## Details", "", body, ""])

    filepath.write_text("\n".join(lines))
    return filepath


def create_change_request(project_dir, to_project, title, body, priority="", blocks=""):
    """Create a CHANGE_REQUEST message in OUTBOX."""
    return _create_collab_message(project_dir, "CHANGE_REQUEST", to_project, title, body, priority=priority, blocks=blocks)


def create_issue_escalation(project_dir, to_project, title, body, priority=""):
    """Create an ISSUE_ESCALATION message in OUTBOX."""
    return _create_collab_message(project_dir, "ISSUE_ESCALATION", to_project, title, body, priority=priority)


def create_status_update(project_dir, to_project, title, body):
    """Create a STATUS_UPDATE message in OUTBOX."""
    return _create_collab_message(project_dir, "STATUS_UPDATE", to_project, title, body)


def create_feedback(project_dir, to_project, title, body, references=""):
    """Create a FEEDBACK message in OUTBOX."""
    return _create_collab_message(project_dir, "FEEDBACK", to_project, title, body, references=references)


def sync_outbox_to_inbox(
    project_dir: Path, project_map: dict[str, Path]
) -> int:
    """Copy OUTBOX files to target project INBOXes.

    project_map: {project_name: project_path}
    Returns count of files synced.
    """
    outbox = project_dir / ".collab" / "OUTBOX"
    if not outbox.exists():
        return 0

    synced = 0
    for f in sorted(outbox.glob("*.md")):
        content = f.read_text()
        meta = parse_collab_file(content)
        target_name = meta.get("to", "")

        if target_name in project_map:
            target_inbox = project_map[target_name] / ".collab" / "INBOX"
            target_inbox.mkdir(parents=True, exist_ok=True)
            target_file = target_inbox / f.name
            if not target_file.exists():
                shutil.copy2(f, target_file)
                synced += 1

    return synced
