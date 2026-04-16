"""Markdown document parser for DevLead.

Parses markdown tables by column header name (not position).
Produces builtin variables for the KPI engine.
"""

import re
from datetime import date
from pathlib import Path


def parse_file_metadata(text: str) -> dict[str, str]:
    """Extract metadata from markdown file header blockquotes.

    Parses lines like:
        # Title Here
        > Type: PROJECT
        > Last updated: 2026-04-05 | Open: 3 | Done: 2

    Returns dict with: title, type, last_updated, and any key-value pairs
    found in the blockquote stats (Open, Done, etc).
    Never crashes on unexpected formats.
    """
    meta: dict[str, str] = {"title": "", "type": "", "last_updated": ""}

    for line in text.splitlines():
        line = line.strip()

        # Title
        if line.startswith("# ") and not meta["title"]:
            meta["title"] = line[2:].strip()

        # Blockquote metadata
        if line.startswith("> "):
            content = line[2:].strip()

            # Type field
            m = re.match(r"Type:\s*(.+)", content)
            if m:
                meta["type"] = m.group(1).strip()
                continue

            # Last updated + inline stats
            m = re.match(r"Last updated:\s*(.+)", content)
            if m:
                parts = m.group(1).split("|")
                meta["last_updated"] = parts[0].strip()
                # Parse inline stats: "Open: 3", "Done: 2", etc.
                for part in parts[1:]:
                    kv = part.strip().split(":", 1)
                    if len(kv) == 2:
                        key = kv[0].strip().lower().replace(" ", "_")
                        meta[key] = kv[1].strip()

    return meta


def parse_table(text: str) -> list[dict[str, str]]:
    """Parse the first markdown table in text into a list of dicts.

    Each dict is keyed by column header name. Returns [] if no table found.
    """
    lines = text.splitlines()

    # Find header row (first line with |)
    header_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            # Check if next line is separator
            if i + 1 < len(lines) and re.match(
                r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1]
            ):
                header_idx = i
                break

    if header_idx is None:
        return []

    # Parse headers
    header_line = lines[header_idx]
    headers = [h.strip() for h in header_line.strip().strip("|").split("|")]

    # Parse data rows (skip separator at header_idx + 1)
    rows = []
    for line in lines[header_idx + 2 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= len(headers):
            row = {headers[j]: cells[j] for j in range(len(headers))}
            rows.append(row)

    return rows


def count_by_status(rows: list[dict], pattern: str) -> int:
    """Count rows where Status column contains pattern (case-insensitive)."""
    count = 0
    for row in rows:
        status = row.get("Status", "")
        if pattern.upper() in status.upper():
            count += 1
    return count


def count_with_pattern(
    rows: list[dict], column: str, regex: str
) -> int:
    """Count rows where column value matches regex."""
    pat = re.compile(regex)
    count = 0
    for row in rows:
        value = row.get(column, "")
        if pat.search(value):
            count += 1
    return count


def count_overdue(
    rows: list[dict], column: str = "Due", today: date | None = None
) -> int:
    """Count rows where date in column is before today.

    Only counts non-DONE/CLOSED tasks.
    """
    if today is None:
        today = date.today()

    count = 0
    for row in rows:
        date_str = row.get(column, "").strip()
        status = row.get("Status", "").upper()

        # Skip done/closed items
        if "DONE" in status or "COMPLETE" in status or "CLOSED" in status:
            continue

        if not date_str or date_str == "—":
            continue

        try:
            due_date = date.fromisoformat(date_str)
            if due_date < today:
                count += 1
        except ValueError:
            continue

    return count


def count_checkboxes(text: str) -> tuple[int, int]:
    """Count done and total checkboxes in text.

    Returns (done, total). Matches `- [x]` and `- [ ]` patterns.
    """
    done = len(re.findall(r"^- \[x\]", text, re.MULTILINE | re.IGNORECASE))
    undone = len(re.findall(r"^- \[ \]", text, re.MULTILINE))
    return done, done + undone


def _read_if_exists(path: Path) -> str:
    """Read file text, return empty string if missing."""
    if path.exists():
        return path.read_text()
    return ""


def _count_intake_status(
    docs_dir: Path, filename: str, status: str
) -> int:
    """Count items with given status in a specific intake file."""
    text = _read_if_exists(docs_dir / filename)
    if not text:
        return 0
    rows = parse_table(text)
    return count_by_status(rows, status)


def _count_table_stats(docs_dir: Path, filename: str) -> dict[str, int]:
    """Count standard PM stats for any file with a Status column."""
    text = _read_if_exists(docs_dir / filename)
    rows = parse_table(text)
    total = len(rows)
    return {
        "total": total,
        "open": count_by_status(rows, "OPEN"),
        "in_progress": count_by_status(rows, "IN_PROGRESS"),
        "done": count_by_status(rows, "DONE"),
        "blocked": count_by_status(rows, "BLOCKED"),
        "reopened": count_by_status(rows, "REOPEN"),
        "active": total - count_by_status(rows, "DONE"),
    }


def get_builtin_vars(
    docs_dir: Path, today: date | None = None
) -> dict[str, int | float]:
    """Compute builtin variables from docs_dir files.

    Three-level hierarchy: Epics → Stories → Tasks.
    Plus aggregate intake counts.
    Missing files produce 0 values (no crash).
    """
    if today is None:
        today = date.today()

    # --- Epics (from _project_roadmap.md) ---
    epic_stats = _count_table_stats(docs_dir, "_project_roadmap.md")

    # --- Stories (from _project_stories.md) ---
    story_stats = _count_table_stats(docs_dir, "_project_stories.md")
    stories_text = _read_if_exists(docs_dir / "_project_stories.md")
    story_rows = parse_table(stories_text)
    stories_with_epic = count_with_pattern(story_rows, "Epic", r"E-\d+")

    # --- Tasks ---
    tasks_text = _read_if_exists(docs_dir / "_project_tasks.md")
    task_rows = parse_table(tasks_text)
    task_stats = _count_table_stats(docs_dir, "_project_tasks.md")
    tasks_overdue = count_overdue(task_rows, "Due", today)
    tasks_with_story = count_with_pattern(task_rows, "Story", r"S-\d+")

    # --- Intake (aggregate across all _intake_*.md files) ---
    intake_open = 0
    intake_closed = 0
    for path in sorted(docs_dir.glob("_intake_*.md")):
        text = path.read_text()
        rows = parse_table(text)
        intake_open += count_by_status(rows, "OPEN")
        intake_closed += count_by_status(rows, "CLOSED")

    intake_total = intake_open + intake_closed

    # --- Derived ---
    stories_total = story_stats["total"]
    stories_done = story_stats["done"]
    convergence = (
        (stories_done / stories_total * 100) if stories_total > 0 else 0
    )

    return {
        # Epics
        "epics_total": epic_stats["total"],
        "epics_open": epic_stats["open"],
        "epics_in_progress": epic_stats["in_progress"],
        "epics_done": epic_stats["done"],
        "epics_blocked": epic_stats["blocked"],
        "epics_active": epic_stats["active"],
        # Stories
        "stories_total": stories_total,
        "stories_open": story_stats["open"],
        "stories_in_progress": story_stats["in_progress"],
        "stories_done": stories_done,
        "stories_blocked": story_stats["blocked"],
        "stories_active": story_stats["active"],
        "stories_with_epic": stories_with_epic,
        # Tasks
        "tasks_total": task_stats["total"],
        "tasks_open": task_stats["open"],
        "tasks_in_progress": task_stats["in_progress"],
        "tasks_done": task_stats["done"],
        "tasks_blocked": task_stats["blocked"],
        "tasks_reopened": task_stats["reopened"],
        "tasks_active": task_stats["active"],
        "tasks_overdue": tasks_overdue,
        "tasks_with_story": tasks_with_story,
        # Intake
        "intake_open": intake_open,
        "intake_closed": intake_closed,
        "intake_total": intake_total,
        # Derived
        "convergence": convergence,
    }


def refresh_intake_header(file_path: Path) -> None:
    """Update intake file header to match actual row counts.

    Reads the file, counts OPEN rows in Active table and rows in Archive,
    then rewrites the header line to match.
    """
    if not file_path.exists():
        return

    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Count active OPEN rows
    rows = parse_table(text)
    open_count = sum(
        1 for r in rows
        if r.get("Status", "").strip().upper() == "OPEN"
    )

    # Count archive rows (second table)
    in_archive = False
    closed_count = 0
    for line in lines:
        if line.strip().startswith("## Archive"):
            in_archive = True
            continue
        if in_archive and line.strip().startswith("|") and not line.strip().startswith("| Key") and not re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
            closed_count += 1

    # Update header line
    for i, line in enumerate(lines):
        if line.strip().startswith("> Last updated:"):
            today = str(date.today())
            lines[i] = f"> Last updated: {today} | Open: {open_count} | Closed: {closed_count}"
            break

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
