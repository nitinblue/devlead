"""Hook output helpers for Claude Code integration.

Claude Code hooks use exit codes to control behavior:
- Exit 0: allow the action, optional JSON on stdout
- Exit 2: block the action, message on stderr
"""
import json
import sys


def hook_allow(message: str = "") -> None:
    """Exit 0 — allows the action. Optional systemMessage in JSON."""
    output = {}
    if message:
        output["systemMessage"] = message
    print(json.dumps(output))
    sys.exit(0)


def hook_block(message: str) -> None:
    """Exit 2 — blocks the action. Message shown to Claude on stderr."""
    print(message, file=sys.stderr)
    sys.exit(2)


def hook_context(context: str) -> None:
    """Exit 0 — allows with context injected into conversation."""
    print(json.dumps({"systemMessage": context}))
    sys.exit(0)
