# _aware_features.md

> **Self-awareness file.** Auto-generated inventory of every feature
> this project exposes. DO NOT EDIT - run `/devlead awareness` to refresh.
> Hand-edits are overwritten on next refresh.
>
> **Last refresh:** 2026-04-16T03:03:15Z
> **Generator:** devlead.awareness v1
> **Scan sources:** commands/*.md, src/devlead/cli.py

---

## Slash commands

### /devlead audit
- **Kind:** slash-command
- **Description:** Inspect the DevLead audit log
- **Command file:** `commands/audit.md`
- **Handler:** `src/devlead/cli.py:_cmd_audit`

### /devlead awareness
- **Kind:** slash-command
- **Description:** Refresh DevLead self-awareness files (_aware_*.md)
- **Command file:** `commands/awareness.md`
- **Handler:** `src/devlead/cli.py:_cmd_awareness`

### /devlead config
- **Kind:** slash-command
- **Description:** Show the resolved DevLead configuration
- **Command file:** `commands/config.md`
- **Handler:** `src/devlead/cli.py:_cmd_config`

### /devlead focus
- **Kind:** slash-command
- **Description:** Set, show, or clear the current focus by flipping intake entry status
- **Command file:** `commands/focus.md`
- **Handler:** `src/devlead/cli.py:_cmd_focus`

### /devlead gate
- **Kind:** slash-command
- **Description:** Run the DevLead PreToolUse enforcement gate (warn-only)
- **Command file:** `commands/gate.md`
- **Handler:** `src/devlead/cli.py:_cmd_gate`

### /devlead ingest
- **Kind:** slash-command
- **Description:** Ingest a plugin's output plan/spec into a DevLead intake file
- **Command file:** `commands/ingest.md`
- **Handler:** `src/devlead/cli.py:_cmd_ingest`

### /devlead init
- **Kind:** slash-command
- **Description:** Install DevLead on the current project — creates devlead_docs/ with scaffolding and seeds the canonical source of truth.
- **Command file:** `commands/init.md`
- **Handler:** `src/devlead/cli.py:_cmd_init`

### /devlead intake
- **Kind:** slash-command
- **Description:** List current intake file entries
- **Command file:** `commands/intake.md`
- **Handler:** `src/devlead/cli.py:_cmd_intake`

### /devlead migrate
- **Kind:** slash-command
- **Description:** Hash-checked, reversible content migration between devlead_docs/ files
- **Command file:** `commands/migrate.md`
- **Handler:** `src/devlead/cli.py:_cmd_migrate`

### /devlead promote
- **Kind:** slash-command
- **Description:** Promote a scratchpad entry to an intake file, a decision log, or a living file
- **Command file:** `commands/promote.md`
- **Handler:** `src/devlead/cli.py:_cmd_promote`

### /devlead scratchpad
- **Kind:** slash-command
- **Description:** Append a raw capture entry to devlead_docs/_scratchpad.md - verbatim triage inbox, zero information loss.
- **Command file:** `commands/scratchpad.md`
- **Handler:** `src/devlead/cli.py:_cmd_scratchpad`

### /devlead triage
- **Kind:** slash-command
- **Description:** Walk untriaged _scratchpad.md entries and route each to its canonical home
- **Command file:** `commands/triage.md`
- **Handler:** `src/devlead/cli.py:_cmd_triage`

### /devlead verify-links
- **Kind:** slash-command
- **Description:** Walk cross-references in devlead_docs/ and report broken refs + orphans
- **Command file:** `commands/verify-links.md`

