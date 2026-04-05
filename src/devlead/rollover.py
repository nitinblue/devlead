"""Monthly rollover — archive closed items, carry forward open items."""

import re
import shutil
from datetime import date
from pathlib import Path

from devlead.doc_parser import parse_table


def do_rollover(
    docs_dir: Path,
    files: list[str],
    today: date | None = None,
) -> None:
    """Roll over specified files: archive full copy, keep only open items.

    Args:
        docs_dir: Path to claude_docs/
        files: List of filenames to roll over
        today: Override date for testing
    """
    if today is None:
        today = date.today()

    month_suffix = today.strftime("%Y-%m")
    archive_dir = docs_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    for fname in files:
        source = docs_dir / fname
        if not source.exists():
            continue

        archive_name = f"{source.stem}_{month_suffix}{source.suffix}"
        archive_path = archive_dir / archive_name

        # Archive: copy full file (only if not already archived this month)
        if not archive_path.exists():
            shutil.copy2(source, archive_path)

        # Rewrite current file: keep only open/active items
        _rewrite_keeping_open(source)


def _rewrite_keeping_open(filepath: Path) -> None:
    """Rewrite a markdown file keeping only open/active rows in its table."""
    text = filepath.read_text()
    lines = text.splitlines()

    # Find the table
    header_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            if i + 1 < len(lines) and re.match(
                r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1]
            ):
                header_idx = i
                break

    if header_idx is None:
        return  # No table, nothing to do

    # Split into: before table, header+separator, data rows, after table
    before = lines[:header_idx]
    header = lines[header_idx]
    separator = lines[header_idx + 1]

    data_rows = []
    after_table_start = header_idx + 2
    for i in range(header_idx + 2, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("|"):
            data_rows.append(lines[i])
            after_table_start = i + 1
        else:
            after_table_start = i
            break
    else:
        after_table_start = len(lines)

    after = lines[after_table_start:]

    # Filter: keep rows that are NOT done/closed/complete
    kept_rows = []
    for row in data_rows:
        # Extract status from the row
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        # Find Status column index from header
        headers = [h.strip() for h in header.strip().strip("|").split("|")]
        status_idx = None
        for j, h in enumerate(headers):
            if h.strip().upper() == "STATUS":
                status_idx = j
                break

        if status_idx is not None and status_idx < len(cells):
            status = cells[status_idx].upper()
            if "DONE" in status or "COMPLETE" in status or "CLOSED" in status:
                continue  # Skip closed items

        kept_rows.append(row)

    # Reconstruct file
    result_lines = before + [header, separator] + kept_rows + after
    filepath.write_text("\n".join(result_lines))
