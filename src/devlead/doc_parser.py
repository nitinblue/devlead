"""Markdown document parser for DevLead.

Parses markdown tables by column header name (not position).
Produces builtin variables for the KPI engine.
"""

import re
from datetime import date
from pathlib import Path


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


def get_builtin_vars(
    docs_dir: Path, today: date | None = None
) -> dict[str, int | float]:
    """Compute all 18 builtin variables from docs_dir files.

    Returns dict with keys matching spec section 8.3.
    Missing files produce 0 values (no crash).
    """
    if today is None:
        today = date.today()

    # --- Tasks ---
    tasks_text = _read_if_exists(docs_dir / "_project_tasks.md")
    task_rows = parse_table(tasks_text)

    tasks_open = count_by_status(task_rows, "OPEN")
    tasks_in_progress = count_by_status(task_rows, "IN_PROGRESS")
    tasks_done = count_by_status(task_rows, "DONE")
    tasks_blocked = count_by_status(task_rows, "BLOCKED")
    tasks_reopened = count_by_status(task_rows, "REOPEN")
    tasks_overdue = count_overdue(task_rows, "Due", today)
    tasks_with_story = count_with_pattern(task_rows, "Story", r"[SE]-\d+")
    tasks_total = len(task_rows)
    tasks_active = tasks_total - tasks_done

    # --- Stories ---
    roadmap_text = _read_if_exists(docs_dir / "_project_roadmap.md")
    stories_done, stories_total = count_checkboxes(roadmap_text)

    # --- Intake (aggregate across all _intake_*.md files) ---
    intake_open = 0
    intake_closed = 0
    for path in sorted(docs_dir.glob("_intake_*.md")):
        text = path.read_text()
        rows = parse_table(text)
        intake_open += count_by_status(rows, "OPEN")
        intake_closed += count_by_status(rows, "CLOSED")

    intake_total = intake_open + intake_closed

    # Specific intake files
    intake_bugs_open = _count_intake_status(docs_dir, "_intake_bugs.md", "OPEN")
    intake_features_open = _count_intake_status(
        docs_dir, "_intake_features.md", "OPEN"
    )
    intake_gaps_open = _count_intake_status(docs_dir, "_intake_gaps.md", "OPEN")

    # --- Derived ---
    convergence = (
        (stories_done / stories_total * 100) if stories_total > 0 else 0
    )

    return {
        "tasks_open": tasks_open,
        "tasks_in_progress": tasks_in_progress,
        "tasks_done": tasks_done,
        "tasks_total": tasks_total,
        "tasks_blocked": tasks_blocked,
        "tasks_reopened": tasks_reopened,
        "tasks_overdue": tasks_overdue,
        "tasks_with_story": tasks_with_story,
        "tasks_active": tasks_active,
        "stories_total": stories_total,
        "stories_done": stories_done,
        "intake_open": intake_open,
        "intake_closed": intake_closed,
        "intake_total": intake_total,
        "intake_bugs_open": intake_bugs_open,
        "intake_features_open": intake_features_open,
        "intake_gaps_open": intake_gaps_open,
        "convergence": convergence,
    }
