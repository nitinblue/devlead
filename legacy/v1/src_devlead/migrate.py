"""DevLead migrate — bootstrap DevLead on an existing project non-destructively.

Scans for existing governance files, creates missing ones, configures hooks,
appends to CLAUDE.md, and reports results. Never overwrites existing files.
"""

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from devlead import ui

# Scaffold directory within the package
SCAFFOLD_DIR = Path(__file__).parent / "scaffold"

# Expected governance files in devlead_docs/
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
    "_living_vision.md",
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
    docs_dir = project_dir / "devlead_docs"
    docs_dir_exists = docs_dir.is_dir()

    # Check devlead_docs/ contents
    if docs_dir_exists:
        for f in sorted(docs_dir.iterdir()):
            if f.is_file() and f.suffix == ".md":
                found.append(f"devlead_docs/{f.name}")

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

    # Create devlead_docs/ if missing
    docs_dir = project_dir / "devlead_docs"
    if not docs_dir.is_dir():
        docs_dir.mkdir(exist_ok=True)
        created.append("devlead_docs/")

    # Create expected doc files if missing
    for fname in EXPECTED_DOC_FILES:
        target = docs_dir / fname
        if target.exists():
            skipped.append(f"devlead_docs/{fname}")
            continue

        source = SCAFFOLD_DIR / fname
        if source.exists():
            content = source.read_text()
            content = content.replace("{date}", today)
            target.write_text(content)
            created.append(f"devlead_docs/{fname}")
        else:
            # Generate a minimal template for files without scaffold
            content = _minimal_template(fname, today)
            target.write_text(content)
            created.append(f"devlead_docs/{fname}")
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

    # Merge hooks into .claude/settings.json
    hooks_result = _merge_hooks(project_dir)
    if hooks_result == "created":
        created.append(".claude/settings.json")
    elif hooks_result == "merged":
        created.append(".claude/settings.json (hooks merged)")
    else:
        skipped.append(".claude/settings.json")

    # Append DevLead section to CLAUDE.md
    claude_result = _append_claude_md(project_dir)
    if claude_result == "created":
        created.append("CLAUDE.md")
    elif claude_result == "appended":
        created.append("CLAUDE.md (DevLead section appended)")
    else:
        skipped.append("CLAUDE.md (DevLead section exists)")

    # Update .gitignore
    _update_gitignore(project_dir)

    # Migrate old BO format if needed
    bo_result = _migrate_bo_format(docs_dir)
    if bo_result:
        warnings.append(bo_result)

    # Write migration audit entries
    _audit_migration(docs_dir, created, skipped, warnings)

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

    docs_dir = project_dir / "devlead_docs"
    if not docs_dir.is_dir():
        would_create.append("devlead_docs/")

    for fname in EXPECTED_DOC_FILES:
        target = docs_dir / fname
        if target.exists():
            already_exists.append(f"devlead_docs/{fname}")
        else:
            would_create.append(f"devlead_docs/{fname}")
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


def _merge_hooks(project_dir: Path) -> str:
    """Merge DevLead hooks into .claude/settings.json. Returns status."""
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    settings_path = claude_dir / "settings.json"

    existing = {}
    was_new = not settings_path.exists()
    if settings_path.exists():
        existing = json.loads(settings_path.read_text())

    hook_source = SCAFFOLD_DIR / "hooks_settings.json"
    if not hook_source.exists():
        return "skipped"
    devlead_hooks = json.loads(hook_source.read_text())["hooks"]

    if "hooks" not in existing:
        existing["hooks"] = {}

    changed = False
    for event, hook_list in devlead_hooks.items():
        if event not in existing["hooks"]:
            existing["hooks"][event] = []

        existing_commands = set()
        for entry in existing["hooks"][event]:
            for h in entry.get("hooks", []):
                existing_commands.add(h.get("command", ""))

        for entry in hook_list:
            for h in entry.get("hooks", []):
                if h.get("command", "") not in existing_commands:
                    existing["hooks"][event].append(entry)
                    changed = True
                    break

    if not changed and not was_new:
        return "skipped"

    settings_path.write_text(json.dumps(existing, indent=2))
    return "created" if was_new else "merged"


_DEVLEAD_CLAUDE_MD_SECTION = """\

## DevLead Governance

> Auto-added by `devlead migrate`. Do not remove.

### Session Start — Mandatory

1. Read `devlead_docs/_project_status.md` — know where we are
2. Read `devlead_docs/_project_tasks.md` — know what's open
3. Read `devlead_docs/_living_standing_instructions.md` — know the rules
4. Read `devlead_docs/_project_roadmap.md` — know the business objectives
5. Scan `devlead_docs/_intake_*.md` — check for new bugs/features
6. Report status to user

### Rules

1. **`devlead_docs/` is the ONLY system of record.** Everything traces to `devlead_docs/`.
2. **Always work in plan mode before code changes.**
3. **Update `devlead_docs/` at session end.** Status, tasks, intake.

### Business Convergence

- Run `devlead status` at session start to see convergence
- Check `devlead_docs/_living_business_objectives.md` for BOs and TBOs
- Every task must trace to a BO. Untraced work is shadow work.
- If no BOs are defined, interview the user before proposing work priorities.
- The model owns TBO decomposition once BOs are frozen.
"""

_DEVLEAD_MARKER = "## DevLead Governance"


def _append_claude_md(project_dir: Path) -> str:
    """Append DevLead section to CLAUDE.md. Returns status."""
    claude_md = project_dir / "CLAUDE.md"

    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if _DEVLEAD_MARKER in content:
            return "skipped"
        if not content.endswith("\n"):
            content += "\n"
        content += _DEVLEAD_CLAUDE_MD_SECTION
        claude_md.write_text(content, encoding="utf-8")
        return "appended"
    else:
        claude_md.write_text(
            f"# {project_dir.name}\n\n"
            + _DEVLEAD_CLAUDE_MD_SECTION,
            encoding="utf-8",
        )
        return "created"


def _audit_migration(
    docs_dir: Path,
    created: list[str],
    skipped: list[str],
    warnings: list[str],
) -> None:
    """Write migration actions to audit log."""
    audit_file = docs_dir / "_audit_log.jsonl"
    now = datetime.now(timezone.utc).isoformat()

    entries = []
    entries.append({
        "timestamp": now,
        "action": "migrate_start",
        "details": {"created_count": len(created), "skipped_count": len(skipped)},
    })
    for item in created:
        entries.append({
            "timestamp": now,
            "action": "migrate_create",
            "file": item,
        })
    for item in skipped:
        entries.append({
            "timestamp": now,
            "action": "migrate_skip",
            "file": item,
        })
    for w in warnings:
        entries.append({
            "timestamp": now,
            "action": "migrate_warning",
            "detail": w,
        })
    entries.append({
        "timestamp": now,
        "action": "migrate_complete",
        "summary": {
            "created": len(created),
            "skipped": len(skipped),
            "warnings": len(warnings),
        },
    })

    with open(audit_file, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def _migrate_bo_format(docs_dir: Path) -> str | None:
    """Migrate old flat TBO format to new BO hierarchy format.

    Returns a description of what changed, or None if no migration needed.
    """
    bo_file = docs_dir / "_living_business_objectives.md"
    if not bo_file.exists():
        return None

    content = bo_file.read_text(encoding="utf-8")

    # If already new format (has BO table with Weight column), skip
    if "| Weight | Status |" in content and "| BO-" in content:
        return None

    # Detect old format: has "## TBOs" or "TBO Tracker" header,
    # or table has "Stories" / "Linked Stories" column
    is_old = False
    if "## TBOs" in content or "## TBO Tracker" in content:
        is_old = True
    if "Linked Stories" in content or "| Stories |" in content:
        is_old = True

    if not is_old:
        return None

    # Parse flat TBO rows from old format
    tbo_rows: list[dict] = []
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        id_cell = cells[0]
        if not re.match(r"TBO-\d+", id_cell):
            continue
        desc = cells[1] if len(cells) > 1 else ""
        status = "NOT_STARTED"
        for cell in cells[2:]:
            cell_upper = cell.upper().strip()
            if cell_upper in (
                "NOT_STARTED", "IN_PROGRESS", "DONE", "BLOCKED", "DRAFT",
            ):
                status = cell_upper
                break
        tbo_rows.append({"id": id_cell, "desc": desc, "status": status})

    if not tbo_rows:
        return None

    # Generate new BO hierarchy format
    today = str(date.today())
    n = len(tbo_rows)
    base_weight = 100 // n if n > 0 else 100
    remainder = 100 - (base_weight * n)

    lines: list[str] = []
    lines.append("# Business Objectives")
    lines.append("")
    lines.append("> Type: LIVING")
    lines.append(f"> Last updated: {today}")
    lines.append("")
    lines.append("## Phase 1")
    lines.append("")
    lines.append("| ID | Objective | Weight | Status |")
    lines.append("|----|-----------|--------|--------|")
    lines.append("| BO-1 | (Migrated from flat TBO format) | 100 | DRAFT |")
    lines.append("")
    lines.append("### BO-1: (Migrated from flat TBO format)")
    lines.append("")
    lines.append("| TBO | Description | Weight | DoD | Status |")
    lines.append("|-----|-------------|--------|-----|--------|")
    for i, tbo in enumerate(tbo_rows):
        w = base_weight + (1 if i < remainder else 0)
        lines.append(
            f"| {tbo['id']} | {tbo['desc']} | {w} | (TBD) | {tbo['status']} |"
        )
    lines.append("")

    bo_file.write_text("\n".join(lines), encoding="utf-8")
    return f"Migrated {n} TBO(s) from flat format to BO hierarchy"


def _update_gitignore(project_dir: Path) -> None:
    """Add session_state.json to .gitignore if not present."""
    gitignore = project_dir / ".gitignore"
    entry = "devlead_docs/session_state.json"

    if gitignore.exists():
        content = gitignore.read_text()
        if entry in content:
            return
        if not content.endswith("\n"):
            content += "\n"
        content += f"{entry}\n"
        gitignore.write_text(content)
    else:
        gitignore.write_text(f"{entry}\n")
