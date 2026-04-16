"""DevLead Level-2 enforcement gate. Implements FEATURES-0004.

Reads a Claude Code hook payload (from stdin via the CLI dispatcher) and
returns a JSON dict describing whether to continue. v1 is warn-only:
`continue` is ALWAYS True. The gate never blocks. This is a locked decision
(see _living_decisions.md and CLAUDE.md "Dev work discipline").

Logic mirrors HTML section 6.3 pseudocode of
docs/memory_and_enforcement_design_2026-04-14.html, but with one substitution:
CWI lives in the intake `status: in_progress` field, NOT in a separate
`_session_state.json`. (Q3 from the design HTML, locked 2026-04-14.)

ASCII only. Stdlib only.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

from devlead import audit, config, intake


_NUDGE = (
    "DevLead discipline: no current working intake is set. "
    "Before editing code, run `/devlead focus <intake-id>` or "
    "create a forced intake entry via "
    "`/devlead ingest --from-scratchpad <needle> --into _intake_features.md --forced`."
)


def check_pretooluse(hook_input: dict, repo_root: Path) -> dict:
    """Run the PreToolUse intake-trace check. Returns a hook-result dict.

    The result always has `continue: True` in warn mode. When discipline is
    not satisfied a `systemMessage` field is included so Claude (and the
    user reading Claude's output) sees the nudge.
    """
    repo_root = Path(repo_root)
    docs_dir = repo_root / "devlead_docs"

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""

    cfg = config.load(repo_root)

    # Exempt-path short circuit (HTML section 6.3 step 1).
    if file_path and _is_exempt(file_path, repo_root, cfg.exempt_paths):
        audit.append_event(
            docs_dir, "gate_pass", tool=tool_name, file=file_path,
            rule="intake_trace", result="exempt",
        )
        return {"continue": True}

    # Look up CWI via intake `status: in_progress` (no _session_state.json).
    in_progress = intake.list_by_status(docs_dir, "in_progress") if docs_dir.exists() else []
    cwi_ids = [entry.id for entry, _path in in_progress]

    if not cwi_ids:
        mode = cfg.enforcement_mode
        audit.append_event(
            docs_dir, "gate_block", tool=tool_name, file=file_path,
            cwi=[], rule="intake_trace", result="blocked", message="no_cwi",
            mode=mode,
        )
        import sys
        print(_NUDGE, file=sys.stderr)
        if mode == "hard":
            sys.exit(2)
        elif mode == "soft":
            sys.exit(1)
        return {"continue": True, "systemMessage": _NUDGE}

    audit.append_event(
        docs_dir, "gate_pass", tool=tool_name, file=file_path,
        cwi=cwi_ids, rule="intake_trace", result="pass",
    )
    return {"continue": True}


def check_session_start(hook_input: dict, repo_root: Path) -> dict:
    """SessionStart hook: inject DevLead context so the LLM knows the rules."""
    from devlead.bootstrap import generate_session_context

    repo_root = Path(repo_root)
    docs_dir = repo_root / "devlead_docs"
    if not docs_dir.exists():
        return {"continue": True}

    context = generate_session_context(docs_dir)
    audit.append_event(docs_dir, "session_start", result="ok")
    return {"continue": True, "systemMessage": context}


def check(hook_name: str, hook_input: dict, repo_root: Path) -> dict:
    """Dispatch by hook name."""
    if hook_name == "PreToolUse":
        return check_pretooluse(hook_input, repo_root)
    if hook_name == "SessionStart":
        return check_session_start(hook_input, repo_root)
    return {"continue": True}


def _is_exempt(file_path: str, repo_root: Path, patterns: list[str]) -> bool:
    """Match `file_path` against exempt globs (absolute and repo-relative)."""
    if not patterns:
        return False
    abs_path = file_path.replace("\\", "/")
    rel_path = abs_path
    try:
        rel = Path(file_path).resolve().relative_to(Path(repo_root).resolve())
        rel_path = str(rel).replace("\\", "/")
    except (ValueError, OSError):
        pass
    bare_name = Path(file_path).name
    for pat in patterns:
        if fnmatch.fnmatch(abs_path, pat):
            return True
        if fnmatch.fnmatch(rel_path, pat):
            return True
        if fnmatch.fnmatch(bare_name, pat):
            return True
    return False
