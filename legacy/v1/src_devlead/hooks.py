"""Hook output helpers for Claude Code integration.

Claude Code hooks use exit codes to control behavior:
- Exit 0: allow the action, optional JSON on stdout
- Exit 2: block the action, message on stderr

All messages are branded with [DevLead] so the model and user
can distinguish DevLead enforcement from model-initiated actions.
"""
import json
import sys

from devlead.ui import hook_msg, hook_err


def hook_allow(message: str = "") -> None:
    """Exit 0 — allows the action. Optional systemMessage in JSON."""
    output = {}
    if message:
        output["systemMessage"] = hook_msg(message)
    print(json.dumps(output))
    sys.exit(0)


def hook_block(message: str) -> None:
    """Exit 2 — blocks the action. Message shown to Claude on stderr."""
    print(hook_err(message), file=sys.stderr)
    sys.exit(2)


def hook_context(context: str) -> None:
    """Exit 0 — allows with context injected into conversation."""
    print(json.dumps({"systemMessage": hook_msg(context)}))
    sys.exit(0)
