"""DevLead init — scaffold project, configure hooks, set up gitignore."""

import json
import shutil
from datetime import date
from pathlib import Path

# Scaffold directory within the package
SCAFFOLD_DIR = Path(__file__).parent / "scaffold"

# Files to copy into claude_docs/
DOC_FILES = [
    "_project_status.md",
    "_project_roadmap.md",
    "_project_stories.md",
    "_project_tasks.md",
    "_intake_issues.md",
    "_intake_features.md",
    "_living_standing_instructions.md",
]

GITIGNORE_ENTRY = "claude_docs/session_state.json"


def do_init(project_dir: Path) -> None:
    """Initialize a DevLead project.

    1. Create claude_docs/ with template files
    2. Create devlead.toml
    3. Merge hooks into .claude/settings.json
    4. Add session_state.json to .gitignore
    """
    today = str(date.today())
    project_name = project_dir.name

    # 1. Create claude_docs/ and copy templates
    docs_dir = project_dir / "claude_docs"
    docs_dir.mkdir(exist_ok=True)

    for fname in DOC_FILES:
        target = docs_dir / fname
        if target.exists():
            continue  # Don't overwrite existing files
        source = SCAFFOLD_DIR / fname
        if source.exists():
            content = source.read_text()
            content = content.replace("{date}", today)
            target.write_text(content)

    # 2. Create devlead.toml
    toml_target = project_dir / "devlead.toml"
    if not toml_target.exists():
        toml_source = SCAFFOLD_DIR / "devlead_toml_template.toml"
        if toml_source.exists():
            content = toml_source.read_text()
            content = content.replace("{project_name}", project_name)
            toml_target.write_text(content)

    # 3. Merge hooks into .claude/settings.json
    _merge_hooks(project_dir)

    # 4. Add to .gitignore
    _update_gitignore(project_dir)

    print(f"DevLead initialized in {project_dir}")
    print(f"  claude_docs/ — {len(list(docs_dir.glob('*.md')))} doc files")
    print(f"  devlead.toml — project configuration")
    print(f"  .claude/settings.json — hooks configured")
    print(f"\nRun 'devlead healthcheck' to verify installation.")


def _merge_hooks(project_dir: Path) -> None:
    """Merge DevLead hooks into .claude/settings.json, preserving existing."""
    claude_dir = project_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    settings_path = claude_dir / "settings.json"

    # Load existing settings
    existing = {}
    if settings_path.exists():
        existing = json.loads(settings_path.read_text())

    # Load DevLead hook template
    hook_source = SCAFFOLD_DIR / "hooks_settings.json"
    devlead_hooks = json.loads(hook_source.read_text())["hooks"]

    # Merge hooks
    if "hooks" not in existing:
        existing["hooks"] = {}

    for event, hook_list in devlead_hooks.items():
        if event not in existing["hooks"]:
            existing["hooks"][event] = []

        # Check which hooks are already present (by command string)
        existing_commands = set()
        for entry in existing["hooks"][event]:
            for h in entry.get("hooks", []):
                existing_commands.add(h.get("command", ""))

        for entry in hook_list:
            for h in entry.get("hooks", []):
                if h.get("command", "") not in existing_commands:
                    existing["hooks"][event].append(entry)
                    break

    settings_path.write_text(json.dumps(existing, indent=2))


def _update_gitignore(project_dir: Path) -> None:
    """Add session_state.json to .gitignore if not already present."""
    gitignore = project_dir / ".gitignore"

    if gitignore.exists():
        content = gitignore.read_text()
        if GITIGNORE_ENTRY in content:
            return  # Already present
        if not content.endswith("\n"):
            content += "\n"
        content += f"{GITIGNORE_ENTRY}\n"
        gitignore.write_text(content)
    else:
        gitignore.write_text(f"{GITIGNORE_ENTRY}\n")
