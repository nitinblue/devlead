"""DevLead doctor — health check for project installation."""

import json
from pathlib import Path


EXPECTED_DOCS = [
    "_project_status.md",
    "_project_roadmap.md",
    "_project_stories.md",
    "_project_tasks.md",
    "_intake_issues.md",
    "_intake_features.md",
    "_living_standing_instructions.md",
]


def do_doctor(project_dir: Path) -> list[dict]:
    """Run health checks on a DevLead project.

    Returns list of dicts with keys: check, status (OK/WARN/ERROR), detail.
    """
    results = []
    docs_dir = project_dir / "claude_docs"

    # 1. claude_docs/ exists
    if docs_dir.is_dir():
        results.append({"check": "claude_docs/ exists", "status": "OK", "detail": ""})
    else:
        results.append({
            "check": "claude_docs/ exists",
            "status": "ERROR",
            "detail": "Run 'devlead init' to create it",
        })
        return results  # No point checking more

    # 2. devlead.toml
    if (project_dir / "devlead.toml").exists():
        results.append({"check": "devlead.toml found", "status": "OK", "detail": ""})
    else:
        results.append({
            "check": "devlead.toml found",
            "status": "WARN",
            "detail": "Using defaults — run 'devlead init' to create",
        })

    # 3. .claude/settings.json has hooks
    settings_path = project_dir / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
            if "hooks" in settings:
                results.append({
                    "check": ".claude/settings.json has hooks",
                    "status": "OK",
                    "detail": "",
                })
            else:
                results.append({
                    "check": ".claude/settings.json has hooks",
                    "status": "WARN",
                    "detail": "No hooks section — run 'devlead init'",
                })
        except json.JSONDecodeError:
            results.append({
                "check": ".claude/settings.json has hooks",
                "status": "WARN",
                "detail": "Invalid JSON",
            })
    else:
        results.append({
            "check": ".claude/settings.json has hooks",
            "status": "WARN",
            "detail": "Not found — run 'devlead init'",
        })

    # 4. session_state.json is gitignored
    gitignore = project_dir / ".gitignore"
    if gitignore.exists() and "session_state.json" in gitignore.read_text():
        results.append({
            "check": "session_state.json is gitignored",
            "status": "OK",
            "detail": "",
        })
    else:
        results.append({
            "check": "session_state.json is gitignored",
            "status": "WARN",
            "detail": "Add 'claude_docs/session_state.json' to .gitignore",
        })

    # 5. Expected doc files
    for fname in EXPECTED_DOCS:
        path = docs_dir / fname
        if path.exists():
            results.append({"check": f"{fname} exists", "status": "OK", "detail": ""})
        else:
            results.append({
                "check": f"{fname} exists",
                "status": "WARN",
                "detail": "Missing — run 'devlead init' to create template",
            })

    return results


def format_doctor(results: list[dict]) -> str:
    """Format doctor results for terminal output."""
    lines = ["", "  DevLead Health Check"]
    for r in results:
        marker = f"[{r['status']}]"
        detail = f" — {r['detail']}" if r["detail"] else ""
        lines.append(f"  {marker:8s} {r['check']}{detail}")
    lines.append("")
    return "\n".join(lines)
