"""Session report generator — derives reports from devlead_docs/ files only.

Never uses model memory. Reads the md files, counts by status,
and produces a branded summary. This is what `devlead report` runs.
"""

from pathlib import Path

from devlead import ui
from devlead.doc_parser import parse_table, parse_file_metadata


def _load_intake(docs_dir: Path, filename: str) -> list[dict[str, str]]:
    """Load and parse an intake file, returning rows."""
    path = docs_dir / filename
    if not path.exists():
        return []
    return parse_table(path.read_text(encoding="utf-8"))


def _load_meta(docs_dir: Path, filename: str) -> dict[str, str]:
    """Load metadata header from a file."""
    path = docs_dir / filename
    if not path.exists():
        return {}
    return parse_file_metadata(path.read_text(encoding="utf-8"))


def _count_status(rows: list[dict], status: str) -> int:
    """Count rows matching a status value."""
    return sum(
        1 for r in rows
        if r.get("Status", "").upper() == status.upper()
    )


def generate_report(docs_dir: Path) -> str:
    """Generate a full session report from devlead_docs/ files.

    Reads: _project_tasks.md, _intake_features.md, _intake_bugs.md,
           _intake_gaps.md, _project_status.md, _project_roadmap.md
    Returns: branded, structured report string.
    """
    lines: list[str] = []
    lines.append(ui.banner())
    lines.append(ui.section("Session Report"))
    lines.append("")

    # --- Tasks ---
    tasks = _load_intake(docs_dir, "_project_tasks.md")
    tasks_meta = _load_meta(docs_dir, "_project_tasks.md")
    t_open = _count_status(tasks, "OPEN")
    t_ip = _count_status(tasks, "IN_PROGRESS")
    t_done = _count_status(tasks, "DONE")
    lines.append(ui.section("Tasks"))
    lines.append(ui.kv("Open", str(t_open)))
    lines.append(ui.kv("In Progress", str(t_ip)))
    lines.append(ui.kv("Done", str(t_done)))
    lines.append(ui.kv("Total", str(len(tasks))))
    if t_open + t_ip > 0:
        for row in tasks:
            if row.get("Status", "").upper() in ("OPEN", "IN_PROGRESS"):
                key = row.get("ID", "?")
                item = row.get("Task", "?")
                status = row.get("Status", "?")
                lines.append(f"  {ui.YELLOW}{key}{ui.RESET} {item} [{status}]")

    # --- Features ---
    feats = _load_intake(docs_dir, "_intake_features.md")
    f_open = _count_status(feats, "OPEN")
    f_closed = _count_status(feats, "CLOSED")
    lines.append(ui.section("Features"))
    lines.append(ui.kv("Open", str(f_open)))
    lines.append(ui.kv("Closed", str(f_closed)))
    lines.append(ui.kv("Total", str(len(feats))))
    p1_feats = [r for r in feats if r.get("Priority", "") == "P1" and r.get("Status", "").upper() == "OPEN"]
    if p1_feats:
        lines.append(f"  {ui.RED}P1 open:{ui.RESET}")
        for row in p1_feats:
            key = row.get("Key", "?")
            item = row.get("Item", "?")
            lines.append(f"    {ui.YELLOW}{key}{ui.RESET} {item}")

    # --- Gaps ---
    gaps = _load_intake(docs_dir, "_intake_gaps.md")
    g_open = _count_status(gaps, "OPEN")
    g_closed = _count_status(gaps, "CLOSED")
    lines.append(ui.section("Gaps"))
    lines.append(ui.kv("Open", str(g_open)))
    lines.append(ui.kv("Closed", str(g_closed)))
    if g_open > 0:
        for row in gaps:
            if row.get("Status", "").upper() == "OPEN":
                key = row.get("Key", "?")
                item = row.get("Item", "?")
                pri = row.get("Priority", "?")
                lines.append(f"  {ui.YELLOW}{key}{ui.RESET} [{pri}] {item}")

    # --- Bugs ---
    bugs = _load_intake(docs_dir, "_intake_bugs.md")
    b_open = _count_status(bugs, "OPEN")
    b_closed = _count_status(bugs, "CLOSED")
    lines.append(ui.section("Bugs"))
    lines.append(ui.kv("Open", str(b_open)))
    lines.append(ui.kv("Closed", str(b_closed)))
    if b_open > 0:
        for row in bugs:
            if row.get("Status", "").upper() == "OPEN":
                key = row.get("Key", "?")
                item = row.get("Item", "?")
                pri = row.get("Priority", "?")
                lines.append(f"  {ui.RED}{key}{ui.RESET} [{pri}] {item}")

    # --- Summary line ---
    total_open = f_open + g_open + b_open + t_open + t_ip
    lines.append(ui.section("Summary"))
    lines.append(ui.kv("Total open items", str(total_open)))
    lines.append(ui.kv("Backlog", f"{f_open} features, {g_open} gaps, {b_open} bugs"))
    if total_open == 0:
        lines.append(ui.ok("All clear."))
    else:
        lines.append(ui.warn(f"{total_open} items need attention."))

    return "\n".join(lines)
