"""Governance enforcement rules for DevLead.

Hard rules that apply regardless of state machine position:
1. No work without a task — Edit/Write blocked if no IN_PROGRESS task
2. Memory derived from docs only — memory writes blocked outside UPDATE
3. Scratchpad for unknowns — capture mechanism for unclassified items

These are configurable via devlead.toml [governance] section.
"""

from pathlib import Path

from devlead.doc_parser import parse_table


def check_active_task(docs_dir: Path) -> dict:
    """Check if there's at least one IN_PROGRESS task in _project_tasks.md.

    Returns dict with:
        has_active: bool — True if an IN_PROGRESS task exists
        active_tasks: list[str] — IDs of active tasks
    """
    tasks_file = docs_dir / "_project_tasks.md"
    if not tasks_file.exists():
        return {"has_active": False, "active_tasks": []}

    text = tasks_file.read_text(encoding="utf-8")
    rows = parse_table(text)

    active = []
    for row in rows:
        status = row.get("Status", "").strip().upper()
        task_id = row.get("ID", "").strip()
        if status == "IN_PROGRESS" and task_id:
            active.append(task_id)

    return {"has_active": len(active) > 0, "active_tasks": active}


def check_intake_current(docs_dir: Path) -> dict:
    """Check if intake files have been updated (not stale).

    Returns dict with:
        files_checked: int
        stale_files: list[str] — filenames that may be stale
    """
    intake_files = [
        "_intake_features.md",
        "_intake_bugs.md",
        "_intake_gaps.md",
    ]
    stale = []
    checked = 0
    for fname in intake_files:
        path = docs_dir / fname
        if path.exists():
            checked += 1
            # A file with 0 rows in Active section could be fine or stale
            # We just check it exists and is parseable
        else:
            stale.append(fname)

    return {"files_checked": checked, "stale_files": stale}


def scratchpad_path(docs_dir: Path) -> Path:
    """Return path to the scratchpad file."""
    return docs_dir / "_scratchpad.md"


def scratchpad_add(docs_dir: Path, item: str, source: str = "model") -> str:
    """Add an item to the scratchpad. Returns the assigned scratch ID."""
    sp = scratchpad_path(docs_dir)

    # Read existing items to determine next ID
    existing_count = 0
    if sp.exists():
        text = sp.read_text(encoding="utf-8")
        rows = parse_table(text)
        existing_count = len(rows)
    else:
        _init_scratchpad(sp)

    scratch_id = f"SCRATCH-{existing_count + 1:03d}"

    # Append row to the table — insert right after the separator line
    text = sp.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Find the separator line (|-----|...) in Active section
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith("|---"):
            # Insert after separator, find the last data row
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            insert_idx = j
            break

    from datetime import date
    new_row = f"| {scratch_id} | {item} | {source} | {date.today()} | PENDING |"
    lines.insert(insert_idx, new_row)

    sp.write_text("\n".join(lines), encoding="utf-8")
    return scratch_id


def scratchpad_list(docs_dir: Path) -> list[dict[str, str]]:
    """List all scratchpad items."""
    sp = scratchpad_path(docs_dir)
    if not sp.exists():
        return []
    text = sp.read_text(encoding="utf-8")
    return parse_table(text)


def scratchpad_clear(docs_dir: Path) -> int:
    """Clear all PENDING items from scratchpad. Returns count cleared."""
    sp = scratchpad_path(docs_dir)
    if not sp.exists():
        return 0

    text = sp.read_text(encoding="utf-8")
    rows = parse_table(text)
    pending = [r for r in rows if r.get("Status", "").upper() == "PENDING"]

    # Rewrite without pending rows
    _init_scratchpad(sp)
    kept = [r for r in rows if r.get("Status", "").upper() != "PENDING"]
    if kept:
        lines = sp.read_text(encoding="utf-8").splitlines()
        insert_idx = len(lines)
        for i, line in enumerate(lines):
            if line.strip().startswith("## Archive"):
                insert_idx = i
                break
        for r in kept:
            row_line = f"| {r.get('Key', '?')} | {r.get('Item', '?')} | {r.get('Source', '?')} | {r.get('Added', '?')} | {r.get('Status', '?')} |"
            lines.insert(insert_idx, row_line)
            insert_idx += 1
        sp.write_text("\n".join(lines), encoding="utf-8")

    return len(pending)


def _init_scratchpad(path: Path) -> None:
    """Create a fresh scratchpad file."""
    path.write_text(
        "# Scratchpad\n\n"
        "> Type: SCRATCHPAD\n"
        "> Items here need triage. Run `devlead triage` to process.\n\n"
        "## Active\n\n"
        "| Key | Item | Source | Added | Status |\n"
        "|-----|------|--------|-------|--------|\n"
        "\n## Archive\n\n"
        "| Key | Item | Triaged To | Resolution |\n"
        "|-----|------|------------|------------|\n",
        encoding="utf-8",
    )
