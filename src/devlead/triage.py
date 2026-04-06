"""Triage scratchpad items into proper intake files.

Reads _scratchpad.md, lets user classify PENDING items as
feature/bug/gap with priority, and moves them to the correct
intake file with a proper key assignment.
"""

import re
from datetime import date
from pathlib import Path

from devlead import ui
from devlead.doc_parser import parse_table

# Intake type -> (filename, key prefix)
INTAKE_MAP = {
    "feature": ("_intake_features.md", "FEAT"),
    "bug": ("_intake_bugs.md", "BUG"),
    "gap": ("_intake_gaps.md", "GAP"),
    "archive": (None, None),  # reject — archive without creating ticket
}

VALID_PRIORITIES = ("P1", "P2", "P3")


def get_pending_items(docs_dir: Path) -> list[dict]:
    """Read scratchpad, return PENDING items."""
    sp = docs_dir / "_scratchpad.md"
    if not sp.exists():
        return []
    text = sp.read_text(encoding="utf-8")
    rows = parse_table(text)
    return [r for r in rows if r.get("Status", "").strip().upper() == "PENDING"]


def get_next_key(docs_dir: Path, intake_type: str) -> str:
    """Scan intake file for highest key number, return next.

    E.g., if highest is FEAT-037, returns "FEAT-038".
    """
    filename, prefix = INTAKE_MAP[intake_type]
    path = docs_dir / filename
    if not path.exists():
        return f"{prefix}-001"

    text = path.read_text(encoding="utf-8")
    # Find all keys matching the prefix pattern across entire file
    pattern = re.compile(rf"{prefix}-(\d+)")
    numbers = [int(m.group(1)) for m in pattern.finditer(text)]

    if not numbers:
        return f"{prefix}-001"

    return f"{prefix}-{max(numbers) + 1:03d}"


def triage_item(
    docs_dir: Path,
    scratch_key: str,
    intake_type: str,
    priority: str,
    item_text: str,
) -> str:
    """Move item from scratchpad to intake file. Returns new key.

    If intake_type is 'archive', rejects the item without creating a ticket.
    """
    if intake_type == "archive":
        _mark_scratchpad_triaged(docs_dir, scratch_key, "ARCHIVED")
        return "ARCHIVED"

    new_key = get_next_key(docs_dir, intake_type)
    today = str(date.today())

    # 1. Append to intake file
    _append_to_intake(docs_dir, intake_type, new_key, item_text, today, priority)

    # 2. Mark scratchpad item as TRIAGED
    _mark_scratchpad_triaged(docs_dir, scratch_key, new_key)

    return new_key


def format_triage_prompt(item: dict) -> str:
    """Format a scratchpad item for display using branded ui output."""
    key = item.get("Key", "?")
    text = item.get("Item", "?")
    source = item.get("Source", "?")
    added = item.get("Added", "?")
    return (
        f"  {ui.YELLOW}{key}{ui.RESET} {text}\n"
        f"    {ui.DIM}Source: {source} | Added: {added}{ui.RESET}"
    )


def format_pending_list(items: list[dict]) -> str:
    """Format all pending items with triage instructions."""
    if not items:
        return ui.info("No pending items in scratchpad.")

    lines = [ui.section("Scratchpad Triage")]
    lines.append(f"  {len(items)} item(s) pending triage:\n")
    for item in items:
        lines.append(format_triage_prompt(item))
    lines.append("")
    lines.append(
        f"  {ui.DIM}Classify with:{ui.RESET}"
        f" devlead triage <SCRATCH-KEY> <feature|bug|gap> <P1|P2|P3>"
    )
    return "\n".join(lines)


def _append_to_intake(
    docs_dir: Path,
    intake_type: str,
    new_key: str,
    item_text: str,
    today: str,
    priority: str,
) -> None:
    """Append a new row to the correct intake file."""
    filename, _prefix = INTAKE_MAP[intake_type]
    path = docs_dir / filename

    if not path.exists():
        _init_intake(path, intake_type)

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Find the separator line in Active section, then find last data row
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith("|---"):
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            insert_idx = j
            break

    new_row = (
        f"| {new_key} | {item_text} | triage | {today}"
        f" | OPEN | {priority} | Triaged from scratchpad |"
    )
    lines.insert(insert_idx, new_row)
    path.write_text("\n".join(lines), encoding="utf-8")


def _mark_scratchpad_triaged(
    docs_dir: Path, scratch_key: str, new_key: str
) -> None:
    """Mark a scratchpad item as TRIAGED and move to archive."""
    sp = docs_dir / "_scratchpad.md"
    if not sp.exists():
        return

    text = sp.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Find the row with this scratch key and remove it
    triaged_item = None
    new_lines = []
    for line in lines:
        if scratch_key in line and line.strip().startswith("|"):
            # Extract item text before removing
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                triaged_item = cells[1]  # Item column
            continue  # Skip this line (remove from active)
        new_lines.append(line)

    # Add to archive section
    if triaged_item:
        archive_idx = None
        for i, line in enumerate(new_lines):
            if line.strip().startswith("|---") and archive_idx is not None:
                # Insert after archive separator
                j = i + 1
                while j < len(new_lines) and new_lines[j].strip().startswith("|"):
                    j += 1
                new_lines.insert(
                    j,
                    f"| {scratch_key} | {triaged_item} | {new_key} | TRIAGED |",
                )
                break
            if "## Archive" in line:
                archive_idx = i

    sp.write_text("\n".join(new_lines), encoding="utf-8")


def _init_intake(path: Path, intake_type: str) -> None:
    """Create a fresh intake file if it doesn't exist."""
    titles = {"feature": "Feature Intake", "bug": "Bug Intake", "gap": "Gap Intake"}
    title = titles.get(intake_type, "Intake")
    path.write_text(
        f"# {title}\n\n"
        f"> Type: INTAKE\n"
        f"> Last updated: {date.today()} | Open: 0 | Closed: 0\n\n"
        "## Active\n\n"
        "| Key | Item | Source | Added | Status | Priority | Notes |\n"
        "|-----|------|--------|-------|--------|----------|-------|\n"
        "\n## Archive\n\n"
        "| Key | Item | Resolved | Resolution |\n"
        "|-----|------|----------|------------|\n",
        encoding="utf-8",
    )
