# _aware_features.md

<!-- devlead:sot
  purpose: "Auto-derived inventory of features (slash commands)"
  owner: "system"
  canonical_for: ["feature_inventory"]
  lineage:
    receives_from: ["commands/ scan"]
    migrates_to: []
  lifetime: "regenerated"
  last_audit: "2026-04-15"
-->


> **Self-awareness file.** Auto-generated inventory of every feature
> this project exposes. DO NOT EDIT - run `/devlead awareness` to refresh.
> Hand-edits are overwritten on next refresh.
>
> **Last refresh:** 2026-04-15T02:05:43Z
> **Generator:** devlead.awareness v1
> **Scan sources:** commands/*.md, src/devlead/cli.py

---

## Slash commands

### /devlead awareness
- **Kind:** slash-command
- **Description:** Refresh DevLead self-awareness files (_aware_*.md)
- **Command file:** `commands/awareness.md`
- **Handler:** `src/devlead/cli.py:_cmd_awareness`

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

### /devlead scratchpad
- **Kind:** slash-command
- **Description:** Append a raw capture entry to devlead_docs/_scratchpad.md - verbatim triage inbox, zero information loss.
- **Command file:** `commands/scratchpad.md`
- **Handler:** `src/devlead/cli.py:_cmd_scratchpad`

### /devlead triage
- **Kind:** slash-command
- **Description:** Walk untriaged _scratchpad.md entries and decide what to do with each
- **Command file:** `commands/triage.md`
- **Handler:** `src/devlead/cli.py:_cmd_triage`

