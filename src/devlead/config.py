"""Configuration management for DevLead.

Reads devlead.toml (Python 3.11+ tomllib), merges with defaults.
"""

import tomllib
from pathlib import Path


DEFAULT_CONFIG: dict = {
    "project": {
        "name": "",
        "docs_dir": "claude_docs",
    },
    "kpis": {
        "circles_warning": 50,
        "ftr_minimum": 60,
        "convergence_target": 80,
    },
    "rollover": {
        "trigger": "date",
        "day_of_month": 1,
        "max_lines": 500,
        "retain_months": 12,
        "files": [
            "_project_tasks.md",
            "_intake_issues.md",
            "_intake_features.md",
        ],
    },
    "scope": {
        "enforcement": "log",  # "log", "warn", "block"
        "auto_clear": True,
    },
    "paths": {
        "memory_policy": "warn",   # "log", "warn", "block" — memory writes outside UPDATE
        "docs_policy": "warn",     # "log", "warn", "block" — claude_docs writes outside UPDATE
    },
    "governance": {
        "task_required": "block",      # "log", "warn", "block" — Edit/Write needs IN_PROGRESS task
        "memory_from_docs": "block",   # "log", "warn", "block" — memory writes only in UPDATE
        "intake_required": "warn",     # "log", "warn", "block" — intake files must exist
    },
    "audit": {
        "enabled": True,
        "cross_project_policy": "log",  # "log", "warn", "block"
    },
    "hooks": {
        "session_start": True,
        "gate_edits": True,
        "gate_plan_mode": True,
        "gate_session_end": True,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursively for nested dicts.

    Lists and scalars in override replace base entirely.
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(
    project_dir: Path, config_name: str = "devlead.toml"
) -> dict:
    """Load config from project_dir/devlead.toml, merged with defaults.

    Returns DEFAULT_CONFIG if no toml file exists.
    """
    toml_path = project_dir / config_name
    if not toml_path.exists():
        return dict(DEFAULT_CONFIG)

    with open(toml_path, "rb") as f:
        user_config = tomllib.load(f)

    return _deep_merge(DEFAULT_CONFIG, user_config)


def get_docs_dir(config: dict, project_dir: Path) -> Path:
    """Resolve the docs directory path."""
    return project_dir / config["project"]["docs_dir"]


def get_state_file(config: dict, project_dir: Path) -> Path:
    """Resolve the session state file path."""
    return get_docs_dir(config, project_dir) / "session_state.json"


def get_kpi_thresholds(config: dict) -> dict:
    """Extract KPI threshold values."""
    return {
        k: v
        for k, v in config["kpis"].items()
        if k != "custom" and k != "plugin"
    }


def get_custom_kpis(config: dict) -> list[dict]:
    """Extract custom KPI definitions from config."""
    return config.get("kpis", {}).get("custom", [])


def get_rollover_config(config: dict) -> dict:
    """Extract rollover configuration."""
    return config["rollover"]


def get_hook_config(config: dict) -> dict:
    """Extract hook configuration."""
    return config["hooks"]
