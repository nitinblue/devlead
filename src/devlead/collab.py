"""Cross-project collaboration channel — .collab/ INBOX/OUTBOX."""

import re
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
        m = re.match(r"^#\s+(REQUEST|FEEDBACK):\s*(.+)", line)
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
