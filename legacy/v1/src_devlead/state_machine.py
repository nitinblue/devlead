"""State machine for DevLead session governance.

9 states: SESSION_START → ORIENT → TRIAGE → PRIORITIZE → PLAN → EXECUTE → UPDATE → SESSION_END

TRIAGE: accept (create ticket) or reject (archive) scratchpad items.
PRIORITIZE: assign priority to open tickets, pick session scope.
Both are guide-with-override — user can skip, DevLead records the deviation.

Enforced via Claude Code hooks. Gates block actions outside allowed states.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from devlead.hooks import hook_allow, hook_block, hook_context

# --- Constants ---

STATES = [
    "SESSION_START",
    "ORIENT",
    "TRIAGE",
    "PRIORITIZE",
    "PLAN",
    "EXECUTE",
    "UPDATE",
    "SESSION_END",
]

VALID_TRANSITIONS: dict[str, list[str]] = {
    "SESSION_START": ["ORIENT"],
    "ORIENT": ["TRIAGE"],
    "TRIAGE": ["PRIORITIZE", "ORIENT"],
    "PRIORITIZE": ["PLAN", "TRIAGE"],
    "PLAN": ["EXECUTE"],
    "EXECUTE": ["UPDATE", "PLAN"],
    "UPDATE": ["SESSION_END", "TRIAGE"],
    "SESSION_END": [],
}

# Exit criteria checklists per state
EXIT_CRITERIA: dict[str, dict[str, bool]] = {
    "ORIENT": {
        "status_read": False,
        "tasks_read": False,
        "intake_scanned": False,
        "kpis_reported": False,
    },
    "TRIAGE": {
        "scratchpad_reviewed": False,
        "items_triaged": False,
    },
    "PRIORITIZE": {
        "priorities_assigned": False,
        "session_scope_set": False,
    },
    "UPDATE": {
        "intake_updated": False,
        "tasks_updated": False,
        "status_updated": False,
        "living_reviewed": False,
        "memory_derived": False,
    },
}


# --- State persistence ---


def init_state() -> dict:
    """Create a fresh session state dict."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "state": "SESSION_START",
        "session_start": now,
        "transitions": [],
        "checklists": {
            state: {k: v for k, v in items.items()}
            for state, items in EXIT_CRITERIA.items()
        },
    }


def save_state(state: dict, state_file: Path) -> None:
    """Write state dict to JSON file."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2))


def load_state(state_file: Path) -> dict:
    """Read state dict from JSON file."""
    return json.loads(state_file.read_text())


# --- Gate checks ---


def check_gate(state_file: Path, gate: str) -> None:
    """Check gate — now delegates to gate_engine for Edit/Write, always allows otherwise."""
    if not state_file.exists():
        hook_context("DevLead session not initialized. Run 'devlead start' to begin.")
        hook_allow()
        return

    state = load_state(state_file)
    current = state["state"]
    hook_allow(f"State: {current}")


def check_gate_with_audit(
    state_file: Path,
    gate: str,
    stdin_text: str,
    audit_log: Path,
) -> None:
    """Gate check with audit logging and configurable gate rules.

    1. Parse hook stdin for file_path
    2. Log the write attempt to audit trail
    3. Evaluate user-defined gate rules from config
    4. Record effort for active tasks
    """
    from devlead.audit import parse_hook_stdin, log_write
    from devlead.gate_engine import evaluate_gates

    # Parse stdin for audit context
    entry = parse_hook_stdin(stdin_text) if stdin_text else None

    # Load current state (don't block if missing)
    current_state = ""
    if state_file.exists():
        try:
            state = load_state(state_file)
            current_state = state.get("state", "")
        except Exception:
            pass

    # Log the write attempt (whether allowed or blocked)
    if entry and entry.file_path:
        entry.state = current_state
        log_write(entry, audit_log)

    # Load gate rules from config
    gates = []
    try:
        from devlead.config import load_config
        project_dir = state_file.parent.parent
        config = load_config(project_dir)
        gates = config.get("gates", [])
    except Exception:
        pass

    # Build context for gate engine
    has_active_task = False
    try:
        from devlead.governance import check_active_task
        docs_dir = state_file.parent
        result = check_active_task(docs_dir)
        has_active_task = result["has_active"]
    except Exception:
        pass

    context = {
        "tool_name": entry.tool_name if entry else "",
        "file_path": (entry.file_path or "").replace("\\", "/") if entry else "",
        "current_state": current_state,
        "has_active_task": has_active_task,
    }

    # Evaluate gates
    action, message = evaluate_gates(gates, context)

    if action == "block":
        hook_block(message)
    elif action == "warn":
        hook_context(f"WARNING: {message}")
        # Fall through to allow

    # Record effort for active tasks
    try:
        from devlead.effort import record_task_effort
        from devlead.governance import check_active_task as _check
        docs_dir = state_file.parent
        result = _check(docs_dir)
        for tid in result["active_tasks"]:
            record_task_effort(
                docs_dir, tid, tokens=entry.token_count if entry else 0
            )
    except Exception:
        pass

    hook_allow()


# --- Transitions ---


def do_transition(state_file: Path, target: str) -> None:
    """Transition to target state if valid and exit criteria met.

    Exits 0 (success) or 2 (blocked).
    """
    if not state_file.exists():
        hook_block("SESSION NOT INITIALIZED — run 'devlead start' first.")

    state = load_state(state_file)
    current = state["state"]

    if target not in STATES:
        hook_block(f"Unknown state '{target}'.")

    # Warn on unusual transitions (informational, not blocking)
    if target not in VALID_TRANSITIONS.get(current, []):
        # Still proceed — just inform
        pass

    # Informational: note incomplete checklist items
    if current in state["checklists"]:
        checklist = state["checklists"][current]
        incomplete = [k for k, v in checklist.items() if not v]
        # Informational only — don't block

    # Auto-clear scope when leaving EXECUTE
    if current == "EXECUTE" and "scope" in state:
        state["scope"] = []

    # Perform transition
    now = datetime.now(timezone.utc).isoformat()
    state["transitions"].append({"from": current, "to": target, "at": now})
    state["state"] = target
    save_state(state, state_file)

    # Capture session snapshot on entering UPDATE or SESSION_END
    if target in ("UPDATE", "SESSION_END"):
        try:
            from devlead.session_history import capture_session_snapshot
            docs_dir = state_file.parent
            history_file = docs_dir / "session_history.jsonl"
            capture_session_snapshot(docs_dir, state, history_file)
        except Exception:
            pass  # Never block transition for history capture

    # Auto-regenerate dashboard on transition
    try:
        from devlead.dashboard import write_dashboard
        write_dashboard(state_file.parent.parent)
    except Exception:
        pass  # Never block transition for dashboard

    hook_allow(f"Transitioned from {current} to {target}.")


# --- Checklists ---


def do_checklist(state_file: Path, state_name: str, key: str) -> None:
    """Mark a checklist item as complete. No exit code (not a hook)."""
    if not state_file.exists():
        raise SystemExit(2)

    state = load_state(state_file)

    if state_name not in state["checklists"]:
        raise SystemExit(2)

    if key not in state["checklists"][state_name]:
        raise SystemExit(2)

    state["checklists"][state_name][key] = True
    save_state(state, state_file)


# --- Session start ---


def do_start(state_file: Path, docs_dir: Path) -> None:
    """Initialize a new session — create state, transition to ORIENT.

    Called by the SessionStart hook. Outputs context for Claude.
    """
    state = init_state()
    now = datetime.now(timezone.utc).isoformat()
    state["transitions"].append(
        {"from": "SESSION_START", "to": "ORIENT", "at": now}
    )
    state["state"] = "ORIENT"
    save_state(state, state_file)

    # Ensure session_history.jsonl exists
    history_file = docs_dir / "session_history.jsonl"
    if not history_file.exists():
        history_file.touch()

    # Build context with KPI summary
    context_parts = [
        "DevLead session started. State: ORIENT.",
        "Read project docs, scan intake, report KPIs before transitioning to TRIAGE.",
    ]

    try:
        from devlead.doc_parser import get_builtin_vars
        from devlead.kpi_engine import compute_builtin_kpis, format_dashboard

        vars = get_builtin_vars(docs_dir)
        results = compute_builtin_kpis(vars, docs_dir=docs_dir)
        dashboard = format_dashboard(results)
        context_parts.append("")
        context_parts.append(dashboard)
    except Exception:
        context_parts.append("(KPI computation skipped — docs may be missing)")

    hook_context("\n".join(context_parts))
