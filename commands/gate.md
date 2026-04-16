---
description: Run the DevLead PreToolUse enforcement gate (warn-only)
---

# /devlead gate

Usage:
  /devlead gate PreToolUse                  # reads hook JSON from stdin, prints result JSON

## What this does

The gate is the programmatic backbone of DevLead's "every code change traces
to an intake entry" rule. It is invoked by Claude Code via a `PreToolUse`
hook in `.claude/settings.json`. Reads the hook payload from stdin, checks
whether any `_intake_*.md` entry currently has `status: in_progress`, and
returns a result JSON with:

- `continue: true` (always - warn mode never blocks)
- `systemMessage` (only when discipline is not satisfied)

Every check writes one event to `devlead_docs/_audit_log.jsonl`
(`gate_pass` or `gate_warn`).

## Locked behavior

- Warn-only. Nothing ever exits non-zero. v1 has no `block` mode.
- Exempt globs default to `devlead_docs/**`, `docs/**`, `*.md`, `commands/**`,
  `tests/**`. Override via `[enforcement] exempt_paths` in `devlead.toml`.
- Focus is read from intake `status: in_progress` only - there is no
  `_session_state.json` file.

## How to enable (manual opt-in)

DevLead does NOT auto-write `.claude/settings.json`. Add the following hook
yourself when you want the discipline signal active:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {"type": "command", "command": "devlead gate PreToolUse", "timeout": 5}
        ]
      }
    ]
  }
}
```
