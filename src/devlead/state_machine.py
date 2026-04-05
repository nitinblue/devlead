"""State machine for DevLead session governance.

7 states: SESSION_START → ORIENT → INTAKE → PLAN → EXECUTE → UPDATE → SESSION_END
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
    "INTAKE",
    "PLAN",
    "EXECUTE",
    "UPDATE",
    "SESSION_END",
]

VALID_TRANSITIONS: dict[str, list[str]] = {
    "SESSION_START": ["ORIENT"],
    "ORIENT": ["INTAKE"],
    "INTAKE": ["PLAN", "ORIENT"],
    "PLAN": ["EXECUTE"],
    "EXECUTE": ["UPDATE", "PLAN"],
    "UPDATE": ["SESSION_END", "INTAKE"],
    "SESSION_END": [],
}

# Gate: which states allow the gated action
GATE_ALLOWS: dict[str, list[str]] = {
    "EXECUTE": ["EXECUTE", "UPDATE"],  # Edit/Write allowed in EXECUTE and UPDATE
    "PLAN": ["INTAKE", "EXECUTE"],  # EnterPlanMode allowed from INTAKE or EXECUTE
    "SESSION_END": STATES,  # Warn only, never block
}

# Exit criteria checklists per state
EXIT_CRITERIA: dict[str, dict[str, bool]] = {
    "ORIENT": {
        "status_read": False,
        "tasks_read": False,
        "intake_scanned": False,
        "kpis_reported": False,
    },
    "INTAKE": {
        "requests_captured": False,
        "triaged": False,
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
    """Check if the current state allows the gated action.

    Exits 0 (allow) or 2 (block). SESSION_END gate always allows (warn only).
    """
    if not state_file.exists():
        hook_block(f"SESSION NOT INITIALIZED — run 'devlead start' first.")

    state = load_state(state_file)
    current = state["state"]

    if gate not in GATE_ALLOWS:
        hook_block(f"Unknown gate '{gate}'.")

    allowed_states = GATE_ALLOWS[gate]

    if gate == "SESSION_END":
        # Warn but don't block
        if current not in ("UPDATE", "SESSION_END"):
            hook_context(
                f"WARNING: Session ending in {current} state. "
                f"Consider transitioning to UPDATE first to update docs."
            )
        else:
            hook_allow()
    elif current in allowed_states:
        hook_allow()
    else:
        hook_block(
            f"BLOCKED: {gate} gate requires state {allowed_states}, "
            f"but current state is {current}."
        )


def check_gate_with_audit(
    state_file: Path,
    gate: str,
    stdin_text: str,
    audit_log: Path,
) -> None:
    """Gate check with audit logging and scope enforcement.

    1. Parse hook stdin for file_path
    2. Log the write attempt to audit trail
    3. Check scope (only in EXECUTE, configurable enforcement)
    4. Check state gate
    """
    from devlead.audit import parse_hook_stdin, log_write
    from devlead.scope import is_in_scope

    # Parse stdin for audit context
    entry = parse_hook_stdin(stdin_text) if stdin_text else None

    # Load current state
    current_state = ""
    scope = []
    scope_enforcement = "log"  # relaxed default
    if state_file.exists():
        state = load_state(state_file)
        current_state = state.get("state", "")
        scope = state.get("scope", [])
        scope_enforcement = state.get("scope_enforcement", "log")

    # Log the write attempt (whether allowed or blocked)
    if entry and entry.file_path:
        entry.state = current_state
        log_write(entry, audit_log)

    # Scope enforcement — only in EXECUTE state
    if (
        current_state == "EXECUTE"
        and scope
        and entry
        and entry.file_path
        and not is_in_scope(entry.file_path, scope, entry.cwd)
    ):
        if scope_enforcement == "block":
            hook_block(
                f"BLOCKED: File outside scope. "
                f"'{entry.file_path}' is not in allowed scope. "
                f"Use 'devlead scope show' to see allowed paths."
            )
        elif scope_enforcement == "warn":
            # Allow but inject warning into conversation
            hook_context(
                f"WARNING: Editing file outside scope: {entry.file_path}. "
                f"Scope allows: {', '.join(scope)}"
            )
        # "log" = silent allow (already logged above)

    # Delegate to state gate check
    check_gate(state_file, gate)


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

    # Check valid transition
    if target not in VALID_TRANSITIONS.get(current, []):
        hook_block(
            f"BLOCKED: Cannot transition from {current} to {target}. "
            f"Valid targets: {VALID_TRANSITIONS.get(current, [])}."
        )

    # Check exit criteria for current state
    if current in state["checklists"]:
        checklist = state["checklists"][current]
        incomplete = [k for k, v in checklist.items() if not v]
        if incomplete:
            hook_block(
                f"BLOCKED: Exit criteria not met for {current}. "
                f"Incomplete: {', '.join(incomplete)}."
            )

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

    # Build context with KPI summary
    context_parts = [
        "DevLead session started. State: ORIENT.",
        "Read project docs, scan intake, report KPIs before transitioning to INTAKE.",
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
