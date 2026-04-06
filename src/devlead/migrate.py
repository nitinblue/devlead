"""DevLead migrate — bootstrap DevLead on an existing project non-destructively.

Scans for existing governance files, creates missing ones, and reports results.
Never overwrites existing files.
"""

from datetime import date
from pathlib import Path

from devlead import ui

# Scaffold directory within the package
SCAFFOLD_DIR = Path(__file__).parent / "scaffold"

# Expected governance files in claude_docs/
EXPECTED_DOC_FILES = [
    "_project_status.md",
    "_project_tasks.md",
    "_project_roadmap.md",
    "_project_stories.md",
    "_intake_features.md",
    "_intake_issues.md",
    "_intake_bugs.md",
    "_intake_gaps.md",
    "_living_standing_instructions.md",
    "_living_business_objectives.md",
    "_living_distribution.md",
]

# Patterns that suggest governance-like files (case-insensitive stems)
_GOVERNANCE_PATTERNS = ["tasks", "roadmap", "status", "intake", "backlog"]


def scan_existing(project_dir: Path) -> dict:
    """Find existing governance-like files in the project.

    Returns dict with:
      found_files: list of str (relative paths of governance files found)
      missing_files: list of str (expected doc files not present)
      docs_dir_exists: bool
    """
    found: list[str] = []
    docs_dir = project_dir / "claude_docs"
    docs_dir_exists = docs_dir.is_dir()

    # Check claude_docs/ contents
    if docs_dir_exists:
        for f in sorted(docs_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                found.append(f"claude_docs/{f.name}")

    # Check CLAUDE.md in root
    claude_md = project_dir / "CLAUDE.md"
    if claude_md.is_file():
        found.append("CLAUDE.md")

    # Check devlead.toml
    if (project_dir / "devlead.toml").is_file():
        found.append("devlead.toml")

    # Check .claude/settings.json
    settings = project_dir / ".claude" / "settings.json"
    if settings.is_file():
        found.append(".claude/settings.json")

    # Scan root for governance-like md files
    for f in sorted(project_dir.iterdir()):
        if not f.is_file() or f.suffix != ".md":
            continue
        if f.name == "CLAUDE.md":
            continue  # already captured
        name_lower = f.name.lower()
        if any(p in name_lower for p in _GOVERNANCE_PATTERNS):
            found.append(f.name)

    # Scan docs/ if it exists
    docs_folder = project_dir / "docs"
    if docs_folder.is_dir():
        for f in sorted(docs_folder.iterdir()):
            if not f.is_file() or f.suffix != ".md":
                continue
            name_lower = f.name.lower()
            if any(p in name_lower for p in _GOVERNANCE_PATTERNS):
                found.append(f"docs/{f.name}")

    # Determine missing expected files
    existing_doc_names = set()
    if docs_dir_exists:
        for f in docs_dir.iterdir():
            if f.is_file():
                existing_doc_names.add(f.name)

    missing = [f for f in EXPECTED_DOC_FILES if f not in existing_doc_names]

    return {
        "found_files": found,
        "missing_files": missing,
        "docs_dir_exists": docs_dir_exists,
    }


def do_migrate(project_dir: Path) -> dict:
    """Non-destructive migration: create missing governance files.

    Returns dict with:
      created: list of str (files created)
      skipped: list of str (files that already existed)
      warnings: list of str
    """
    today = str(date.today())
    project_name = project_dir.name
    created: list[str] = []
    skipped: list[str] = []
    warnings: list[str] = []

    # Create claude_docs/ if missing
    docs_dir = project_dir / "claude_docs"
    if not docs_dir.is_dir():
        docs_dir.mkdir(exist_ok=True)
        created.append("claude_docs/")

    # Create expected doc files if missing
    for fname in EXPECTED_DOC_FILES:
        target = docs_dir / fname
        if target.exists():
            skipped.append(f"claude_docs/{fname}")
            continue

        source = SCAFFOLD_DIR / fname
        if source.exists():
            content = source.read_text()
            content = content.replace("{date}", today)
            target.write_text(content)
            created.append(f"claude_docs/{fname}")
        else:
            # Generate a minimal template for files without scaffold
            content = _minimal_template(fname, today)
            target.write_text(content)
            created.append(f"claude_docs/{fname}")
            warnings.append(
                f"No scaffold template for {fname} -- created minimal placeholder"
            )

    # Create devlead.toml if missing
    toml_target = project_dir / "devlead.toml"
    if toml_target.exists():
        skipped.append("devlead.toml")
    else:
        toml_source = SCAFFOLD_DIR / "devlead_toml_template.toml"
        if toml_source.exists():
            content = toml_source.read_text()
            content = content.replace("{project_name}", project_name)
            toml_target.write_text(content)
            created.append("devlead.toml")
        else:
            warnings.append("No scaffold template for devlead.toml")

    return {
        "created": created,
        "skipped": skipped,
        "warnings": warnings,
    }


def do_migrate_dry_run(project_dir: Path) -> dict:
    """Preview what migrate would do without writing anything.

    Returns dict with:
      would_create: list of str
      already_exists: list of str
      warnings: list of str
    """
    would_create: list[str] = []
    already_exists: list[str] = []
    warnings: list[str] = []

    docs_dir = project_dir / "claude_docs"
    if not docs_dir.is_dir():
        would_create.append("claude_docs/")

    for fname in EXPECTED_DOC_FILES:
        target = docs_dir / fname
        if target.exists():
            already_exists.append(f"claude_docs/{fname}")
        else:
            would_create.append(f"claude_docs/{fname}")
            if not (SCAFFOLD_DIR / fname).exists():
                warnings.append(f"No scaffold for {fname} -- will use minimal template")

    toml_target = project_dir / "devlead.toml"
    if toml_target.exists():
        already_exists.append("devlead.toml")
    else:
        would_create.append("devlead.toml")

    return {
        "would_create": would_create,
        "already_exists": already_exists,
        "warnings": warnings,
    }


def format_migration_report(result: dict) -> str:
    """Format migration result as branded terminal output."""
    lines: list[str] = []
    lines.append(ui.section("Migration Report"))

    # Handle both dry-run and real results
    created = result.get("created") or result.get("would_create") or []
    skipped = result.get("skipped") or result.get("already_exists") or []
    warnings = result.get("warnings", [])
    is_dry_run = "would_create" in result

    if is_dry_run:
        lines.append(f"  {ui.DIM}(dry run -- no files written){ui.RESET}")
        lines.append("")

    if created:
        label = "Would create" if is_dry_run else "Created"
        lines.append(f"  {ui.BOLD}{label}:{ui.RESET}")
        for f in created:
            lines.append(f"    {ui.GREEN}{ui.ICON_OK}{ui.RESET} {f}")
    else:
        lines.append(f"  {ui.DIM}Nothing to create.{ui.RESET}")

    if skipped:
        label = "Already exists" if is_dry_run else "Skipped (existing)"
        lines.append(f"\n  {ui.BOLD}{label}:{ui.RESET}")
        for f in skipped:
            lines.append(f"    {ui.CYAN}{ui.ICON_BULLET}{ui.RESET} {f}")

    if warnings:
        lines.append(f"\n  {ui.BOLD}Warnings:{ui.RESET}")
        for w in warnings:
            lines.append(f"    {ui.YELLOW}{ui.ICON_WARN}{ui.RESET} {w}")

    total_created = len(created)
    total_skipped = len(skipped)
    if is_dry_run:
        summary = f"{total_created} file(s) to create, {total_skipped} already present"
    else:
        summary = f"{total_created} file(s) created, {total_skipped} skipped"
    lines.append("")
    lines.append(ui.ok(summary))

    return "\n".join(lines)


def _minimal_template(filename: str, today: str) -> str:
    """Generate a minimal markdown template for files without a scaffold."""
    # Derive a title from the filename
    name = filename.replace(".md", "").replace("_", " ").strip().title()

    if "intake" in filename.lower():
        return (
            f"# {name}\n\n"
            f"> Type: INTAKE\n"
            f"> Last updated: {today} | Open: 0 | Closed: 0\n\n"
            f"## Active\n\n"
            f"| Key | Item | Source | Added | Status | Priority | Notes |\n"
            f"|-----|------|--------|-------|--------|----------|-------|\n\n"
            f"## Archive\n\n"
            f"| Key | Item | Resolved | Resolution |\n"
            f"|-----|------|----------|------------|\n"
        )
    else:
        return f"# {name}\n\n> Last updated: {today}\n"
