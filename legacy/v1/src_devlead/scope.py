"""Scope lock — define and enforce which files the AI can touch.

Scope is stored in session_state.json. Only enforced during EXECUTE state.
Empty scope = everything allowed (backwards compatible).
"""

import json
from pathlib import Path, PurePosixPath


def set_scope(state_file: Path, paths: list[str]) -> None:
    """Set the allowed file/directory scope."""
    state = json.loads(state_file.read_text())
    state["scope"] = paths
    state_file.write_text(json.dumps(state, indent=2))


def get_scope(state_file: Path) -> list[str]:
    """Get the current scope. Returns [] if no scope set."""
    if not state_file.exists():
        return []
    state = json.loads(state_file.read_text())
    return state.get("scope", [])


def clear_scope(state_file: Path) -> None:
    """Remove scope lock."""
    if not state_file.exists():
        return
    state = json.loads(state_file.read_text())
    state["scope"] = []
    state_file.write_text(json.dumps(state, indent=2))


def is_in_scope(
    file_path: str,
    scope: list[str],
    project_dir: str,
) -> bool:
    """Check if a file_path is within the allowed scope.

    Returns True if:
    - scope is empty (no restriction)
    - file_path matches any scope entry (exact file or under directory)

    All paths normalized to forward slashes for comparison.
    """
    if not scope:
        return True

    # Normalize to forward slashes
    norm_file = file_path.replace("\\", "/")
    norm_project = project_dir.rstrip("/\\").replace("\\", "/")

    # Get relative path from project dir
    if norm_file.startswith(norm_project):
        rel_path = norm_file[len(norm_project):].lstrip("/")
    else:
        rel_path = norm_file

    for entry in scope:
        norm_entry = entry.replace("\\", "/")
        if norm_entry.endswith("/"):
            # Directory scope — check prefix
            if rel_path.startswith(norm_entry):
                return True
        else:
            # Exact file match
            if rel_path == norm_entry:
                return True

    return False
