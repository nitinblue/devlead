---
description: Show the resolved DevLead configuration
---

# /devlead config

Usage:
  /devlead config show                      # pretty-print the resolved config

## What this does

Loads `devlead.toml` from the repo root (if present), merges it onto the
in-code defaults from `src/devlead/config.py`, and prints the resolved
sections (memory, enforcement, audit, intake).

The TOML file is OPTIONAL. Every knob has a default in code; the file only
overrides what you uncomment. Parsed via stdlib `tomllib` (Python 3.11+) -
zero external dependencies.

## Where to put your overrides

A scaffold template ships at `src/devlead/scaffold/devlead.toml.tmpl` with
every default commented out. Copy it to your repo root as `devlead.toml`,
uncomment the lines you care about, and edit. (It is NOT auto-installed by
`devlead init` yet - see FEATURES-0009 follow-up.)
