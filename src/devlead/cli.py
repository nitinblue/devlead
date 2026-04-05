"""DevLead CLI entry point."""

import sys
from pathlib import Path

from devlead import __version__

COMMANDS = [
    "init",
    "start",
    "status",
    "gate",
    "transition",
    "checklist",
    "kpis",
    "rollover",
    "healthcheck",
    "portfolio",
    "collab",
    "audit",
    "scope",
    "dashboard",
]

USAGE = f"""\
devlead {__version__} — Lead your development. Don't let AI wander.

Usage: devlead <command> [options]

Commands:
  init          Initialize a new project
  start         Start a session
  status        Show project status
  gate          Run a phase gate check
  transition    Transition to next phase
  checklist     Show/verify phase checklist
  kpis          Show project KPIs
  rollover      Roll incomplete work forward
  healthcheck   Diagnose project health
  portfolio     Manage multi-project portfolio
  collab        Cross-repo collaboration
  audit         Show file write audit log
  scope         Set/show/clear file scope lock
  dashboard     Generate HTML session report

Options:
  --help        Show this help message
  --version     Show version
"""


def main() -> None:
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(USAGE)
        return

    if "--version" in args:
        print(f"devlead {__version__}")
        return

    command = args[0]
    if command not in COMMANDS:
        print(f"devlead: unknown command '{command}'", file=sys.stderr)
        print("Run 'devlead --help' for usage.", file=sys.stderr)
        sys.exit(1)

    # Resolve project paths
    docs_dir = Path.cwd() / "claude_docs"
    state_file = docs_dir / "session_state.json"

    if command == "init":
        from devlead.init import do_init
        do_init(Path.cwd())
        return
    elif command == "start":
        from devlead.state_machine import do_start
        do_start(state_file, docs_dir)
    elif command == "gate":
        if len(args) < 2:
            print("Usage: devlead gate <EXECUTE|PLAN|SESSION_END>", file=sys.stderr)
            sys.exit(1)
        # Read hook stdin for audit context
        stdin_text = ""
        if not sys.stdin.isatty():
            stdin_text = sys.stdin.read()
        audit_log = docs_dir / "_audit_log.jsonl"
        from devlead.state_machine import check_gate_with_audit
        check_gate_with_audit(state_file, args[1], stdin_text, audit_log)
    elif command == "transition":
        if len(args) < 2:
            print("Usage: devlead transition <STATE>", file=sys.stderr)
            sys.exit(1)
        from devlead.state_machine import do_transition
        do_transition(state_file, args[1])
    elif command == "checklist":
        if len(args) < 3:
            print("Usage: devlead checklist <STATE> <KEY>", file=sys.stderr)
            sys.exit(1)
        from devlead.state_machine import do_checklist
        do_checklist(state_file, args[1], args[2])
    elif command == "status":
        _cmd_status(state_file, docs_dir)
    elif command == "kpis":
        _cmd_kpis(docs_dir)
    elif command == "rollover":
        _cmd_rollover(docs_dir)
    elif command == "healthcheck":
        _cmd_healthcheck()
    elif command == "portfolio":
        _cmd_portfolio(args[1:])
    elif command == "collab":
        _cmd_collab(args[1:])
    elif command == "audit":
        _cmd_audit(docs_dir)
    elif command == "scope":
        _cmd_scope(args[1:], state_file)
    elif command == "dashboard":
        _cmd_dashboard()
    else:
        print(f"devlead: '{command}' not yet implemented.")


def _cmd_status(state_file: Path, docs_dir: Path) -> None:
    """Show current state + summary KPIs."""
    from devlead.state_machine import load_state, VALID_TRANSITIONS
    from devlead.doc_parser import get_builtin_vars
    from devlead.kpi_engine import compute_builtin_kpis

    if not state_file.exists():
        print("No active session. Run 'devlead start' first.", file=sys.stderr)
        sys.exit(1)

    state = load_state(state_file)
    current = state["state"]
    next_states = VALID_TRANSITIONS.get(current, [])

    vars = get_builtin_vars(docs_dir)
    results = compute_builtin_kpis(vars, docs_dir=docs_dir)

    # Find key metrics
    convergence = next((r for r in results if r.name == "Code-Domain Convergence"), None)
    throughput = next((r for r in results if r.name == "Intake Throughput"), None)
    nba = next((r for r in results if r.name == "Next Best Action"), None)

    print(f"State: {current} | Next: {', '.join(next_states)}")
    print(f"Pipeline: {vars.get('tasks_open', 0)} open | "
          f"{vars.get('tasks_in_progress', 0)} in progress | "
          f"{vars.get('tasks_done', 0)} done")
    if convergence:
        print(f"Convergence: {convergence.value:.0f}/100")
    if throughput:
        print(f"Intake: {throughput.value:.0f}% closed")
    if nba and nba.detail:
        print(f">> {nba.detail}")


def _cmd_kpis(docs_dir: Path) -> None:
    """Show full KPI dashboard."""
    from datetime import date
    from devlead.config import load_config, get_custom_kpis
    from devlead.doc_parser import get_builtin_vars
    from devlead.kpi_engine import compute_all_kpis, format_dashboard

    project_dir = docs_dir.parent
    config = load_config(project_dir)
    custom_defs = get_custom_kpis(config)

    vars = get_builtin_vars(docs_dir)
    results = compute_all_kpis(vars, docs_dir=docs_dir, custom_defs=custom_defs or None)
    print(format_dashboard(results, project_date=str(date.today())))


def _cmd_rollover(docs_dir: Path) -> None:
    """Run monthly rollover."""
    from devlead.config import load_config, get_rollover_config
    from devlead.rollover import do_rollover

    project_dir = docs_dir.parent
    config = load_config(project_dir)
    rollover_config = get_rollover_config(config)
    files = rollover_config.get("files", [])

    do_rollover(docs_dir, files)
    print(f"Rollover complete. {len(files)} files processed.")


def _cmd_healthcheck() -> None:
    """Run health check."""
    from devlead.doctor import do_doctor, format_doctor

    project_dir = Path.cwd()
    results = do_doctor(project_dir)
    print(format_doctor(results))


def _cmd_portfolio(sub_args: list[str]) -> None:
    """Manage multi-project portfolio."""
    from devlead.portfolio import (
        add_project, remove_project, list_projects,
        compute_portfolio_kpis, format_portfolio_dashboard,
    )

    workspace = Path.home() / ".devlead"

    if not sub_args:
        # Show portfolio dashboard
        projects = list_projects(workspace)
        results = compute_portfolio_kpis(workspace)
        print(format_portfolio_dashboard(projects, results))
        return

    subcmd = sub_args[0]

    if subcmd == "add":
        if len(sub_args) < 2:
            print("Usage: devlead portfolio add <path> [--name <name>]", file=sys.stderr)
            sys.exit(1)
        path = sub_args[1]
        name = sub_args[3] if len(sub_args) > 3 and sub_args[2] == "--name" else Path(path).name
        add_project(workspace, path, name)
        print(f"Added '{name}' to portfolio.")
    elif subcmd == "remove":
        if len(sub_args) < 2:
            print("Usage: devlead portfolio remove <name>", file=sys.stderr)
            sys.exit(1)
        remove_project(workspace, sub_args[1])
        print(f"Removed '{sub_args[1]}' from portfolio.")
    elif subcmd == "list":
        projects = list_projects(workspace)
        if not projects:
            print("No projects registered. Use 'devlead portfolio add <path>'.")
        else:
            for p in projects:
                print(f"  {p['name']:<20} {p['path']}")
    else:
        print(f"Unknown portfolio subcommand: {subcmd}", file=sys.stderr)
        sys.exit(1)


def _cmd_collab(sub_args: list[str]) -> None:
    """Cross-project collaboration."""
    from devlead.collab import init_collab, scan_inbox, collab_status

    project_dir = Path.cwd()

    if not sub_args or sub_args[0] == "status":
        status = collab_status(project_dir)
        print(f"Collab: {status['inbox_count']} inbox | {status['outbox_count']} outbox | {status['open_requests']} open requests")
    elif sub_args[0] == "init":
        init_collab(project_dir)
        print("Collab channel initialized (.collab/INBOX/ and .collab/OUTBOX/).")
    elif sub_args[0] == "inbox":
        items = scan_inbox(project_dir)
        if not items:
            print("Inbox is empty.")
        else:
            for item in items:
                status_mark = "!!" if item.get("status", "").upper() == "OPEN" else "  "
                print(f"  {status_mark} {item['filename']} — {item.get('type', '?')}: {item.get('title', '?')} [{item.get('status', '?')}]")
    elif sub_args[0] == "sync":
        from devlead.collab import sync_outbox_to_inbox
        from devlead.portfolio import list_projects
        workspace = Path.home() / ".devlead"
        projects = list_projects(workspace)
        project_map = {p["name"]: Path(p["path"]) for p in projects}
        synced = sync_outbox_to_inbox(project_dir, project_map)
        print(f"Synced {synced} message(s) to target project inboxes.")
    else:
        print(f"Unknown collab subcommand: {sub_args[0]}", file=sys.stderr)
        sys.exit(1)


def _cmd_audit(docs_dir: Path) -> None:
    """Show audit log."""
    from devlead.audit import read_audit_log

    log_file = docs_dir / "_audit_log.jsonl"
    records = read_audit_log(log_file)

    if not records:
        print("No audit entries.")
        return

    for r in records:
        ts = r.get("timestamp", "?")[:19]
        tool = r.get("tool_name", "?")
        fp = r.get("file_path", "?")
        state = r.get("state", "?")
        cross = " [CROSS-PROJECT]" if r.get("cross_project") else ""
        agent = f" (agent: {r['agent_type']})" if r.get("agent_type") else ""
        print(f"  {ts} | {state:<10} | {tool:<6} | {fp}{cross}{agent}")


def _cmd_scope(sub_args: list[str], state_file: Path) -> None:
    """Manage scope lock."""
    from devlead.scope import set_scope, get_scope, clear_scope

    if not sub_args or sub_args[0] == "show":
        scope = get_scope(state_file)
        if not scope:
            print("No scope set. All files are editable during EXECUTE.")
        else:
            print("Scope lock active. Allowed paths:")
            for p in scope:
                print(f"  {p}")
    elif sub_args[0] == "set":
        if len(sub_args) < 2:
            print("Usage: devlead scope set <path1> [path2] ...", file=sys.stderr)
            sys.exit(1)
        set_scope(state_file, sub_args[1:])
        print(f"Scope set: {len(sub_args) - 1} path(s) allowed.")
        for p in sub_args[1:]:
            print(f"  {p}")
    elif sub_args[0] == "clear":
        clear_scope(state_file)
        print("Scope cleared. All files are editable during EXECUTE.")
    else:
        print(f"Unknown scope subcommand: {sub_args[0]}", file=sys.stderr)
        sys.exit(1)


def _cmd_dashboard() -> None:
    """Generate HTML session report."""
    from devlead.dashboard import write_dashboard

    project_dir = Path.cwd()
    path = write_dashboard(project_dir)
    print(f"Dashboard generated: {path}")
    print(f"Open in browser: file:///{path.as_posix()}")
