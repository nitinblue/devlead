---
description: Inspect the DevLead audit log
---

# /devlead audit

Usage:
  /devlead audit recent [N]                 # print the last N events (default 20)

## What this does

Tails `devlead_docs/_audit_log.jsonl` and prints one JSON event per line.
Newest events are at the bottom (the file is append-only).

Events are written by every command that mutates state: `ingest`,
`ingest_from_scratchpad`, `promote_to_living`, `focus_change`,
`awareness_refresh`, `gate_pass`, `gate_warn`. Schema is locked per HTML
section 8.1 of `docs/memory_and_enforcement_design_2026-04-14.html`:

    {ts, event, tool?, cwi?, intake_id?, source?, origin?, result?,
     message?, file?, rule?}

## Why a JSONL log

- Append-only - no read/modify cycles, no corruption surface.
- One event per line - easy to grep, easy to tail.
- Stable schema - feeds future KPIs (K_BYPASS, drift, BO yield) without
  re-instrumentation.
