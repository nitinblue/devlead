"""Smart project analysis — TBO-by-TBO assessment tied to business outcomes.

Reads ALL project docs: TBOs, stories, tasks, distribution, scratchpad.
Produces a structured analysis showing convergence, blockers, and next actions.
"""

import re
from pathlib import Path

from devlead import ui
from devlead.doc_parser import parse_table, count_by_status


def _read(path: Path) -> str:
    """Read file text, empty string if missing."""
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _parse_tbo_stories(linked: str) -> list[str]:
    """Extract story IDs from a TBO's Linked Stories field."""
    return re.findall(r"S-\d+", linked) if linked else []


def _section_tables(text: str) -> dict[str, list[dict[str, str]]]:
    """Parse multiple tables from distribution doc, keyed by ## heading."""
    sections: dict[str, list[dict[str, str]]] = {}
    heading = ""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## ") and not line.startswith("## What"):
            heading = line[3:].strip()
            i += 1
            continue
        if (heading and line.startswith("|") and i + 1 < len(lines)
                and re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i + 1])):
            table_lines = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                table_lines.append(lines[j])
                j += 1
            sections[heading] = parse_table("\n".join(table_lines))
            i = j
            continue
        i += 1
    return sections


def _assess_tbo(tbo: dict, story_map: dict, task_rows: list[dict]) -> dict:
    """Build assessment for a single TBO."""
    tbo_id = tbo.get("ID", "?")
    status = tbo.get("Status", "OPEN")
    linked_ids = _parse_tbo_stories(tbo.get("Linked Stories", ""))
    stories_total = len(linked_ids)
    stories_done = sum(1 for s in linked_ids
                       if story_map.get(s, "").upper() in ("DONE", "COMPLETE"))

    # Find open/blocked tasks linked to this TBO's stories
    open_count, blocked = 0, []
    for t in task_rows:
        t_ids = re.findall(r"S-\d+", t.get("Story", ""))
        if not any(s in linked_ids for s in t_ids):
            continue
        t_status = t.get("Status", "").upper()
        if t_status in ("OPEN", "IN_PROGRESS"):
            open_count += 1
        if t_status == "BLOCKED":
            blocked.append(f"{t.get('ID', '?')}: {t.get('Blockers', '?')}")

    # Determine assessment
    if status.upper() == "DONE":
        assessment = "COMPLETE"
    elif stories_total > 0 and stories_done == stories_total and not open_count:
        assessment = "READY FOR ACCEPTANCE -- needs user sign-off"
    elif stories_total > 0 and stories_done == stories_total:
        assessment = f"STORIES DONE -- {open_count} task(s) still open"
    elif stories_total == 0:
        assessment = "NOT STARTED -- needs story breakdown"
    elif stories_done > 0:
        assessment = f"IN PROGRESS -- {stories_done}/{stories_total} stories done"
    else:
        assessment = "OPEN -- no stories completed yet"

    blockers = blocked[:]
    if stories_total == 0:
        blockers.append("No stories linked")

    return {
        "id": tbo_id, "objective": tbo.get("Objective", "?"),
        "status": status, "stories_done": stories_done,
        "stories_total": stories_total, "open_tasks": open_count,
        "blockers": blockers, "assessment": assessment,
    }


def _detect_shadow_work(task_rows: list[dict]) -> list[dict]:
    """Find non-DONE tasks with no story link."""
    return [t for t in task_rows
            if t.get("Status", "").upper() != "DONE"
            and not re.search(r"S-\d+", t.get("Story", ""))]


def generate_analysis(docs_dir: Path) -> str:
    """Generate full TBO-driven project analysis."""
    lines: list[str] = [ui.banner()]

    # --- Load all data ---
    tbo_rows = parse_table(_read(docs_dir / "_living_business_objectives.md"))
    story_rows = parse_table(_read(docs_dir / "_project_stories.md"))
    story_map = {r.get("ID", ""): r.get("Status", "") for r in story_rows}
    task_rows = parse_table(_read(docs_dir / "_project_tasks.md"))
    dist_sections = _section_tables(_read(docs_dir / "_living_distribution.md"))
    scratch_rows = parse_table(_read(docs_dir / "_scratchpad.md"))
    scratch_pending = count_by_status(scratch_rows, "PENDING")

    # --- TBO Analysis ---
    lines.append(ui.section("Project Analysis"))
    tbo_done = sum(1 for t in tbo_rows if t.get("Status", "").upper() == "DONE")
    tbo_total = len(tbo_rows)
    pct = int(tbo_done / tbo_total * 100) if tbo_total else 0
    lines += ["", ui.kv("Convergence", f"{tbo_done}/{tbo_total} TBOs ({pct}%)"), ""]

    for tbo in tbo_rows:
        a = _assess_tbo(tbo, story_map, task_rows)
        lines.append(
            f"  {ui.BOLD}{ui.CYAN}{a['id']}{ui.RESET}"
            f": {a['objective']} {ui.GRAY}[{a['status']}]{ui.RESET}")
        lines.append(ui.kv("    Stories", f"{a['stories_done']}/{a['stories_total']} done"))
        lines.append(ui.kv("    Open tasks", str(a["open_tasks"])))
        blocker_str = ", ".join(a["blockers"]) if a["blockers"] else "None"
        lines.append(ui.kv("    Blockers", blocker_str))
        lines.append(f"    {ui.YELLOW}Assessment:{ui.RESET} {a['assessment']}")
        lines.append("")

    # --- Distribution Status ---
    lines.append(ui.section("Distribution Status"))
    dist_labels = {
        "Open Source Compliance": "Compliance",
        "Package Build and Upload": "Package",
        "Revenue Infrastructure": "Revenue",
        "Marketing": "Marketing",
    }
    for sect, label in dist_labels.items():
        rows = dist_sections.get(sect, [])
        done = sum(1 for r in rows if r.get("Status", "").upper() == "DONE")
        lines.append(ui.kv(f"  {label}", f"{done}/{len(rows)} done"))

    # --- Shadow Work ---
    lines.append(ui.section("Shadow Work"))
    shadow = _detect_shadow_work(task_rows)
    if shadow:
        lines.append(f"  {len(shadow)} task(s) have no story link (shadow work)")
        for t in shadow:
            lines.append(
                f"    {ui.YELLOW}{t.get('ID', '?')}{ui.RESET}"
                f" {t.get('Task', '?')} [{t.get('Status', '?')}]")
    else:
        lines.append(ui.ok("No shadow work detected."))

    # --- Scratchpad ---
    lines.append(ui.section("Scratchpad"))
    if scratch_pending > 0:
        lines.append(f"  {scratch_pending} item(s) pending triage")
    else:
        lines.append(ui.ok("Scratchpad clear."))

    return "\n".join(lines)
