"""Install command - creates devlead_docs/ in a target project and copies scaffold templates.

Idempotent: re-running install on an already-installed project reports what already
exists and does not overwrite user content. Only creates files that are missing.
Supports nested target paths (parent directories are mkdir'd on demand).
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


SCAFFOLD_DIR = Path(__file__).parent / "scaffold"

# Files copied from scaffold/ into devlead_docs/ at install time.
# Each entry is (scaffold_relative_path, target_relative_path). Paths with
# sub-directories are supported; parent dirs are created on demand.
#
# Implements FEATURES-0012: only three _living_*.md files ship by default.
# The rest are available via install_addon() — created on demand so a fresh
# install doesn't feel like empty-placeholder busywork.
SCAFFOLD_FILES: list[tuple[str, str]] = [
    ("_project_status.md.tmpl",                 "_project_status.md"),
    ("_project_hierarchy.md.tmpl",              "_project_hierarchy.md"),
    ("_living_project.md.tmpl",                 "_living_project.md"),
    ("_living_standing_instructions.md.tmpl",   "_living_standing_instructions.md"),
    ("_living_decisions.md.tmpl",               "_living_decisions.md"),
    ("_resume.md.tmpl",                         "_resume.md"),
    ("_scratchpad.md.tmpl",                     "_scratchpad.md"),
    ("_intake_features.md.tmpl",                "_intake_features.md"),
    ("_intake_bugs.md.tmpl",                    "_intake_bugs.md"),
    ("_intake_templates/default.md.tmpl",       "_intake_templates/default.md"),
    ("_aware_features.md.tmpl",                 "_aware_features.md"),
    ("_aware_design.md.tmpl",                   "_aware_design.md"),
    ("_routing_table.md.tmpl",                  "_routing_table.md"),
]

# On-demand living files. Slug -> (scaffold template, target filename).
# Not installed by default; user opts in via `devlead init --add <slug>` (CLI
# wiring is a follow-up). The .tmpl files remain in scaffold/ so this lookup
# always works. See FEATURES-0012.
LIVING_ADDONS: dict[str, tuple[str, str]] = {
    "goals":    ("_living_goals.md.tmpl",    "_living_goals.md"),
    "metrics":  ("_living_metrics.md.tmpl",  "_living_metrics.md"),
    "technical":("_living_technical.md.tmpl","_living_technical.md"),
    "design":   ("_living_design.md.tmpl",   "_living_design.md"),
    "glossary": ("_living_glossary.md.tmpl", "_living_glossary.md"),
    "risks":    ("_living_risks.md.tmpl",    "_living_risks.md"),
}

EMPTY_FILES: list[str] = [
    "_audit_log.jsonl",
    "_promise_ledger.jsonl",
]

INTERVIEW_TEMPLATE_NAME = "interview_template.md"


@dataclass
class InstallReport:
    target_dir: Path
    created: list[str] = field(default_factory=list)
    skipped_exists: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        lines = [f"DevLead install -> {self.target_dir}"]
        if self.created:
            lines.append(f"  Created ({len(self.created)}):")
            for f in self.created:
                lines.append(f"    + {f}")
        if self.skipped_exists:
            lines.append(f"  Skipped, already exists ({len(self.skipped_exists)}):")
            for f in self.skipped_exists:
                lines.append(f"    = {f}")
        if self.errors:
            lines.append(f"  Errors ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"    ! {e}")
        if not self.created and not self.errors:
            lines.append("  Nothing to do - project already has devlead_docs/.")
        return "\n".join(lines)


def install(target_dir: Path | None = None) -> InstallReport:
    """Install DevLead onto target_dir (defaults to cwd).

    Creates devlead_docs/ with scaffold templates, empty jsonl logs, the
    interview template, and the intake-template directory. Idempotent.
    """
    target_dir = Path(target_dir).resolve() if target_dir else Path.cwd().resolve()
    report = InstallReport(target_dir=target_dir)

    if not target_dir.exists():
        report.errors.append(f"target directory does not exist: {target_dir}")
        return report

    docs_dir = target_dir / "devlead_docs"
    try:
        docs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        report.errors.append(f"cannot create devlead_docs/: {e}")
        return report

    # Copy scaffold templates. Supports nested target paths.
    for scaffold_name, target_name in SCAFFOLD_FILES:
        src = SCAFFOLD_DIR / scaffold_name
        dst = docs_dir / target_name
        if dst.exists():
            report.skipped_exists.append(target_name)
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            if target_name == "_project_status.md":
                _stamp_install_time(dst)
            report.created.append(target_name)
        except OSError as e:
            report.errors.append(f"cannot create {target_name}: {e}")

    # Create empty jsonl files.
    for empty_name in EMPTY_FILES:
        dst = docs_dir / empty_name
        if dst.exists():
            report.skipped_exists.append(empty_name)
            continue
        try:
            dst.touch()
            report.created.append(empty_name)
        except OSError as e:
            report.errors.append(f"cannot create {empty_name}: {e}")

    # Copy the interview template.
    interview_src = SCAFFOLD_DIR / INTERVIEW_TEMPLATE_NAME
    interview_dst = docs_dir / INTERVIEW_TEMPLATE_NAME
    if interview_dst.exists():
        report.skipped_exists.append(INTERVIEW_TEMPLATE_NAME)
    else:
        try:
            shutil.copyfile(interview_src, interview_dst)
            report.created.append(INTERVIEW_TEMPLATE_NAME)
        except OSError as e:
            report.errors.append(f"cannot create {INTERVIEW_TEMPLATE_NAME}: {e}")

    # Generate/update CLAUDE.md with the DevLead governance section.
    try:
        from devlead.bootstrap import write_claude_md
        msg = write_claude_md(target_dir)
        report.created.append(msg)
    except Exception as e:
        report.errors.append(f"CLAUDE.md generation: {e}")

    # Wire SessionStart + PreToolUse hooks into .claude/settings.json.
    try:
        _wire_hooks(target_dir)
        report.created.append(".claude/settings.json: hooks wired")
    except Exception as e:
        report.errors.append(f"hook wiring: {e}")

    return report


def _stamp_install_time(status_file: Path) -> None:
    """Replace the install placeholder in _project_status.md with the actual timestamp."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    content = status_file.read_text(encoding="utf-8")
    content = content.replace("(set at install)", now)
    status_file.write_text(content, encoding="utf-8")


def _wire_hooks(target_dir: Path) -> None:
    """Create or update .claude/settings.json with DevLead hooks."""
    import json

    settings_dir = target_dir / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings_path = settings_dir / "settings.json"

    if settings_path.exists():
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        data = {}

    hooks = data.setdefault("hooks", {})

    session_hook = {
        "matcher": "",
        "hooks": [{
            "type": "command",
            "command": "python -m devlead gate SessionStart",
            "timeout": 5,
        }],
    }
    pretool_hook = {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{
            "type": "command",
            "command": "python -m devlead gate PreToolUse",
            "timeout": 5,
        }],
    }

    def _has_devlead_hook(hook_list: list) -> bool:
        for h in hook_list:
            for sub in h.get("hooks", []):
                if "devlead gate" in sub.get("command", ""):
                    return True
        return False

    session_list = hooks.setdefault("SessionStart", [])
    if not _has_devlead_hook(session_list):
        session_list.append(session_hook)

    pretool_list = hooks.setdefault("PreToolUse", [])
    if not _has_devlead_hook(pretool_list):
        pretool_list.append(pretool_hook)

    settings_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def install_addon(target_dir: Path, slug: str) -> str:
    """Install an on-demand _living_<slug>.md from the scaffold. FEATURES-0012.

    Looks up LIVING_ADDONS[slug] for curated templates, or falls back to any
    matching `_living_<slug>.md.tmpl` in the scaffold directory (permissive —
    users may ship custom templates). Skips (no-op) if the file already exists.
    """
    target_dir = Path(target_dir).resolve()
    docs_dir = target_dir / "devlead_docs"
    if not docs_dir.exists():
        raise FileNotFoundError(
            f"devlead_docs/ not found at {docs_dir}; run `devlead init` first"
        )

    if slug in LIVING_ADDONS:
        scaffold_name, target_name = LIVING_ADDONS[slug]
    else:
        candidate = f"_living_{slug}.md.tmpl"
        if (SCAFFOLD_DIR / candidate).exists():
            scaffold_name, target_name = candidate, f"_living_{slug}.md"
        else:
            known = ", ".join(sorted(LIVING_ADDONS.keys()))
            raise ValueError(
                f"unknown living addon slug: {slug!r} (known: {known})"
            )

    src = SCAFFOLD_DIR / scaffold_name
    dst = docs_dir / target_name
    if dst.exists():
        return f"skipped (already exists): {target_name}"

    shutil.copyfile(src, dst)
    return f"added: {target_name}"
