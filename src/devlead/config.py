"""DevLead config loader. Implements FEATURES-0009.

Reads `devlead.toml` from the repo root via stdlib `tomllib` (Python 3.11+).
Defaults live in code; the TOML file overrides any subset of them. Zero deps.

Layout mirrors HTML section 7 of docs/memory_and_enforcement_design_2026-04-14.html:

    [memory]
    resume_bloat_cap_lines = 50
    scratchpad_archive_after_sprints = 1

    [enforcement]
    mode = "warning"                 # warning | soft | hard
    exempt_paths = ["devlead_docs/**", "docs/**", "*.md",
                    "commands/**", "tests/**"]

    [audit]
    log_file = "devlead_docs/_audit_log.jsonl"
    retention_days = 365

    [intake]
    actionable_items_min = 1

ASCII only. Stdlib only. On a missing or malformed file the loader falls back
to defaults and prints a one-line warning to stderr; it never raises.
"""

from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


DEFAULTS: dict = {
    "memory": {
        "resume_bloat_cap_lines": 50,
        "scratchpad_archive_after_sprints": 1,
    },
    "enforcement": {
        "mode": "warning",
        "exempt_paths": [
            "devlead_docs/**",
            "docs/**",
            "*.md",
            "commands/**",
            "tests/**",
        ],
    },
    "audit": {
        "log_file": "devlead_docs/_audit_log.jsonl",
        "retention_days": 365,
    },
    "intake": {
        "actionable_items_min": 1,
    },
}


@dataclass
class Config:
    repo_root: Path
    data: dict = field(default_factory=dict)

    def section(self, name: str) -> dict:
        return dict(self.data.get(name, {}))

    def get(self, dotted: str, default=None):
        cur = self.data
        for part in dotted.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    # Typed accessors -------------------------------------------------
    @property
    def resume_bloat_cap_lines(self) -> int:
        return int(self.get("memory.resume_bloat_cap_lines", 50))

    @property
    def scratchpad_archive_after_sprints(self) -> int:
        return int(self.get("memory.scratchpad_archive_after_sprints", 1))

    @property
    def enforcement_mode(self) -> str:
        return str(self.get("enforcement.mode", "warning"))

    @property
    def exempt_paths(self) -> list[str]:
        v = self.get("enforcement.exempt_paths", DEFAULTS["enforcement"]["exempt_paths"])
        return list(v) if isinstance(v, (list, tuple)) else []

    @property
    def audit_log_file(self) -> str:
        return str(self.get("audit.log_file", "devlead_docs/_audit_log.jsonl"))

    @property
    def audit_retention_days(self) -> int:
        return int(self.get("audit.retention_days", 365))

    @property
    def intake_actionable_items_min(self) -> int:
        return int(self.get("intake.actionable_items_min", 1))


def _deep_merge(base: dict, override: dict) -> dict:
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in base.items()}
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load(repo_root: Path) -> Config:
    """Load `devlead.toml` from `repo_root`. Falls back to defaults if absent."""
    repo_root = Path(repo_root)
    cfg_path = repo_root / "devlead.toml"
    merged = _deep_merge(DEFAULTS, {})
    if cfg_path.exists():
        try:
            with cfg_path.open("rb") as fh:
                user = tomllib.load(fh)
            merged = _deep_merge(merged, user)
        except (tomllib.TOMLDecodeError, OSError) as e:
            print(f"devlead: warning: failed to parse {cfg_path}: {e}", file=sys.stderr)
    return Config(repo_root=repo_root, data=merged)
