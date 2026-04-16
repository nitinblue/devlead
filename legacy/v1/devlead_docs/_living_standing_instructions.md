# Standing Instructions

> Type: LIVING
> Last updated: 2026-04-05

## devlead_docs/ Is the ONLY System of Record

1. **`devlead_docs/` is what gets checked into the repo.** No exceptions. This is the single source of truth for all project governance.

2. **`docs/superpowers/` files are working artifacts (scratch paper).** Specs and plans created by superpowers skills MUST be digested into `devlead_docs/` files during the UPDATE state. The superpowers files are NOT the system of record.

3. **Memory (`~/.claude/memory/`) is derived from `devlead_docs/` only.** Memory never contains standalone knowledge. It's a thin index pointing to `devlead_docs/` files.

4. **This makes the project agnostic of any plugin.** If superpowers is uninstalled, `devlead_docs/` still works. If DevLead is uninstalled, `devlead_docs/` files are still readable markdown. No vendor lock-in.

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

## Two Tracks: Business vs Technical

14. **TBO (Tangible Business Outcome) is the unit of business progress.** A TBO is written from the end user's perspective -- what they can do now that they couldn't before. TBOs live in `_living_business_objectives.md`. Each TBO links to the stories that must be delivered before it's considered done. TBOs are the ONLY thing tracked in the progress timeline.

15. **Epic/Story/Task is all technical -- these are "enablers."** Epics categorize technical work (by team, area, theme). Stories are technical deliverables. Tasks are implementation steps. None of these are business progress by themselves. They are enablers -- necessary work that enables TBOs, but not progress until a TBO moves.

16. **Every task is classified as: Functional, Non-Functional, or Shadow Work.**
    - **Functional** = directly delivers user-facing capability. Task → Story → TBO chain is traceable.
    - **Non-Functional** = infrastructure, refactoring, performance, testing, tooling. Supports delivery indirectly. Task → Story link exists but the work isn't user-visible.
    - **Shadow Work** = task that contributes to no TBO. Always bad -- wasted effort, wasted tokens, wasted time.
    - Classification lives at the task level. Each task belongs to a story. Each story feeds one or more TBOs. If a task's story has no TBO link, the task is shadow work by definition.

17. **Convergence = TBOs done / TBOs total.** Not stories. Not tasks. A TBO is done when ALL its linked stories are delivered AND the user can actually do the thing described. 100 stories delivered with 0 TBOs completed = 0% convergence.

17. **The dashboard bookends are the truth.** Business tab (first, TBOs) and Distribution tab (last, productionization) are what matters. Everything in between is operational detail.

## Book of Work

19. **Every dev work gets a task ticket first.** No exceptions. Before any file is created or edited, a TASK-* entry must exist in `_project_tasks.md` with status IN_PROGRESS. No ticket = no work. This applies to all work -- functional, non-functional, model-initiated or user-requested.

20. **The task gate enforces this.** DevLead blocks Edit/Write if no IN_PROGRESS task exists in `_project_tasks.md`. The model cannot bypass this.

## Rollover Policy

18. **Rollover triggers:** Configurable in `devlead.toml` -- either by date (first of month) OR by file size (when file exceeds N lines). Default: date-based. Config:
    ```toml
    [rollover]
    trigger = "date"       # "date" or "size"
    day_of_month = 1       # for date trigger
    max_lines = 500        # for size trigger
    ```
