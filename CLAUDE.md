# CLAUDE.md — DevLead

## What This Project Is

DevLead is a Python CLI tool that provides **project governance for AI-assisted development.** It enforces a state machine via Claude Code hooks so AI assistants can't go rogue.

Tagline: **"Lead your development. Don't let AI wander."**

## Session Start — Mandatory

1. Read `claude_docs/_project_status.md` — know where we are
2. Read `claude_docs/_project_tasks.md` — know what's open
3. Read `claude_docs/_living_standing_instructions.md` — know the rules
4. Read `claude_docs/_project_roadmap.md` — know the business objectives
5. Scan `claude_docs/_intake_*.md` — check for new bugs/features
6. Report status to user

## Rules

1. **`claude_docs/` is the ONLY system of record.** Not `docs/superpowers/`. Not `~/.claude/memory/`. Everything traces to `claude_docs/`.
2. **Always work in plan mode before code changes.**
3. **TDD throughout.** Write failing tests first.
4. **Zero external dependencies.** Python stdlib only (3.11+).
5. **Subagent-driven execution** for implementation plan tasks.
6. **Update `claude_docs/` at session end.** Status, tasks, intake.

## Key Files

- `claude_docs/_project_tasks.md` — active backlog (12 tasks)
- `claude_docs/_project_roadmap.md` — epics, stories, objectives
- `claude_docs/_living_standing_instructions.md` — 14 standing rules
- `docs/2026-04-05-devlead-design.md` — design spec (reference, not system of record)
- `docs/superpowers/plans/2026-04-05-devlead-implementation.md` — implementation plan (reference)

## Dev Commands

```bash
pip install -e .                           # install locally
devlead --help                             # CLI help
devlead --version                          # version
python -m pytest tests/ -v                 # run all tests
python -m pytest tests/test_hooks.py -v    # run specific test
```

## Architecture

```
src/devlead/
├── __init__.py          # version
├── __main__.py          # python -m devlead
├── cli.py               # CLI dispatch
├── hooks.py             # Hook output helpers (DONE)
├── state_machine.py     # States, transitions, gates (TODO)
├── config.py            # devlead.toml parsing (TODO)
├── doc_parser.py        # Markdown table parsing (TODO)
├── kpi_engine.py        # 30 KPIs + custom + plugins (TODO)
├── rollover.py          # Monthly archival (TODO)
├── portfolio.py         # Multi-project (TODO)
├── collab.py            # Cross-project channel (TODO)
└── scaffold/            # Templates for devlead init (TODO)
```
