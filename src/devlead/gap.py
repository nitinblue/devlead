"""DevLead gap analysis — automated governance gap detection.

Scans claude_docs/ for: missing files, shadow work (tasks without
Story linkage), orphan stories, intake count mismatches, file size
violations.
"""

from pathlib import Path

from devlead.doc_parser import parse_table, parse_file_metadata


# Files that a well-governed project should have
EXPECTED_FILES = [
    "_living_standing_instructions.md",
    "_living_business_objectives.md",
    "_project_roadmap.md",
    "_project_stories.md",
    "_project_tasks.md",
    "_project_status.md",
    "_intake_features.md",
    "_intake_bugs.md",
]

MAX_FILE_LINES = 200


def run_gap_analysis(project_dir: Path) -> list[dict]:
    """Run full governance gap analysis.

    Returns list of gap dicts with keys: id, category, severity, message.
    """
    docs_dir = project_dir / "claude_docs"
    gaps: list[dict] = []

    if not docs_dir.is_dir():
        _add(gaps, "MISSING_FILE", "P1",
             "claude_docs/ directory not found")
        return gaps

    _check_missing_files(docs_dir, gaps)
    _check_shadow_work(docs_dir, gaps)
    _check_orphan_stories(docs_dir, gaps)
    _check_intake_mismatches(docs_dir, gaps)
    _check_file_sizes(project_dir, gaps)

    return gaps


def _add(gaps: list[dict], category: str, severity: str,
         message: str) -> dict:
    """Create and append a gap dict with auto-incremented ID."""
    g = {
        "id": f"GAP-{len(gaps) + 1:03d}",
        "category": category,
        "severity": severity,
        "message": message,
    }
    gaps.append(g)
    return g


def _check_missing_files(docs_dir: Path, gaps: list[dict]) -> None:
    for fname in EXPECTED_FILES:
        if not (docs_dir / fname).exists():
            _add(gaps, "MISSING_FILE", "P2",
                 f"Missing expected file: {fname}")


def _check_shadow_work(docs_dir: Path, gaps: list[dict]) -> None:
    tasks_file = docs_dir / "_project_tasks.md"
    if not tasks_file.exists():
        return

    text = tasks_file.read_text(encoding="utf-8")
    rows = parse_table(text)

    for row in rows:
        task_id = row.get("ID", "").strip()
        story = row.get("Story", "").strip()
        status = row.get("Status", "").strip().upper()

        # Skip done tasks
        if "DONE" in status or "CLOSED" in status:
            continue

        if not story or story == "\u2014" or story == "-":
            _add(gaps, "SHADOW_WORK", "P1",
                 f"Task {task_id} has no Story linkage (shadow work)")


def _check_orphan_stories(docs_dir: Path, gaps: list[dict]) -> None:
    stories_file = docs_dir / "_project_stories.md"
    if not stories_file.exists():
        return

    text = stories_file.read_text(encoding="utf-8")
    rows = parse_table(text)

    for row in rows:
        story_id = row.get("ID", "").strip()
        epic = row.get("Epic", "").strip()
        status = row.get("Status", "").strip().upper()

        if "DONE" in status or "CLOSED" in status:
            continue

        if not epic or epic == "\u2014" or epic == "-":
            _add(gaps, "ORPHAN_STORY", "P1",
                 f"Story {story_id} has no Epic/TBO linkage")


def _check_intake_mismatches(docs_dir: Path, gaps: list[dict]) -> None:
    for path in sorted(docs_dir.glob("_intake_*.md")):
        text = path.read_text(encoding="utf-8")
        meta = parse_file_metadata(text)
        rows = parse_table(text)

        # Check "Open" header stat vs actual open rows
        _check_stat(gaps, path.name, meta, rows, "open", "OPEN")
        _check_stat(gaps, path.name, meta, rows, "closed", "CLOSED")


def _check_stat(gaps: list[dict], fname: str,
                meta: dict, rows: list[dict],
                meta_key: str, status_pattern: str) -> None:
    """Compare a header stat count against actual row count."""
    header_val = meta.get(meta_key, "")
    if not header_val:
        return

    try:
        expected = int(header_val)
    except ValueError:
        return

    actual = 0
    for row in rows:
        if status_pattern.upper() in row.get("Status", "").upper():
            actual += 1

    if expected != actual:
        _add(gaps, "INTAKE_MISMATCH", "P2",
             f"{fname}: header says {meta_key}={expected}, "
             f"actual rows={actual}")


def _check_file_sizes(project_dir: Path, gaps: list[dict]) -> None:
    src_dir = project_dir / "src" / "devlead"
    if not src_dir.is_dir():
        return

    for py_file in sorted(src_dir.glob("*.py")):
        try:
            line_count = len(py_file.read_text(encoding="utf-8").splitlines())
        except (OSError, UnicodeDecodeError):
            continue

        if line_count > MAX_FILE_LINES:
            _add(gaps, "FILE_SIZE", "P2",
                 f"{py_file.name}: {line_count} lines "
                 f"(max {MAX_FILE_LINES})")


def format_gaps(gaps: list[dict]) -> str:
    """Format gap results for terminal display using ui module."""
    from devlead import ui

    if not gaps:
        return ui.ok("No governance gaps detected.")

    lines = [ui.section("Gap Analysis")]
    p1 = [g for g in gaps if g["severity"] == "P1"]
    p2 = [g for g in gaps if g["severity"] == "P2"]

    if p1:
        lines.append(f"\n  {ui.RED}{ui.BOLD}P1 — Requires Attention{ui.RESET}")
        for g in p1:
            lines.append(f"  {ui.RED}{g['id']}{ui.RESET} "
                         f"[{g['category']}] {g['message']}")

    if p2:
        lines.append(f"\n  {ui.YELLOW}{ui.BOLD}P2 — Advisory{ui.RESET}")
        for g in p2:
            lines.append(f"  {ui.YELLOW}{g['id']}{ui.RESET} "
                         f"[{g['category']}] {g['message']}")

    lines.append("")
    total = len(gaps)
    lines.append(ui.kv("Total gaps", f"{total} ({len(p1)} P1, {len(p2)} P2)"))
    return "\n".join(lines)
