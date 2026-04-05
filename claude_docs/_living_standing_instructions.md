# Standing Instructions

> Type: LIVING
> Last updated: 2026-04-05

## claude_docs/ Is the ONLY System of Record

1. **`claude_docs/` is what gets checked into the repo.** No exceptions. This is the single source of truth for all project governance.

2. **`docs/superpowers/` files are working artifacts (scratch paper).** Specs and plans created by superpowers skills MUST be digested into `claude_docs/` files during the UPDATE state. The superpowers files are NOT the system of record.

3. **Memory (`~/.claude/memory/`) is derived from `claude_docs/` only.** Memory never contains standalone knowledge. It's a thin index pointing to `claude_docs/` files.

4. **This makes the project agnostic of any plugin.** If superpowers is uninstalled, `claude_docs/` still works. If DevLead is uninstalled, `claude_docs/` files are still readable markdown. No vendor lock-in.

## Execution

5. **Always use subagent-driven execution for implementation plans.** Dispatch one subagent per task, review between tasks.

6. **Always work in plan mode before code changes.** No exceptions.

7. **TDD throughout.** Write failing tests first, then implement.

## Quality

8. **Zero external dependencies.** Python stdlib only (3.11+). No pip deps.

9. **All functions take Path parameters.** No module-level globals for file paths. Makes testing trivial.

10. **Parse by column header name, not position.** Markdown tables may have columns in any order.

11. **No `eval()`.** Formula evaluator must be a safe recursive descent parser.

## Documentation

12. **Update `_project_status.md` at session end.** What was accomplished, what's next.

13. **Register discoveries in `_intake_*.md` immediately.** Don't wait until session end.

## Rollover Policy

14. **Rollover triggers:** Configurable in `devlead.toml` — either by date (first of month) OR by file size (when file exceeds N lines). Default: date-based. Config:
    ```toml
    [rollover]
    trigger = "date"       # "date" or "size"
    day_of_month = 1       # for date trigger
    max_lines = 500        # for size trigger
    ```
