"""DevLead CLI entry point."""

import sys

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
    "doctor",
    "portfolio",
    "collab",
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
  doctor        Diagnose project health
  portfolio     Manage multi-project portfolio
  collab        Cross-repo collaboration

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

    # Commands will be implemented in future tasks
    print(f"devlead: '{command}' not yet implemented.")
