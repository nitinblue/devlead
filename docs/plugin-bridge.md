# Plugin Bridge - how DevLead and other plugins coexist

## TL;DR

DevLead is the single source of truth for a project's work backlog,
but it does not replace other Claude Code plugins. Plugins run exactly
as they always have. DevLead ingests their output files into
`devlead_docs/_intake_*.md` AFTER the plugin has finished. Every task
that ever gets coded traces back to a canonical node in `devlead_docs/`.
No "dark code".

## Why this matters

Without a bridge, work done through other plugins lives outside
DevLead's visibility. Plans get written, code gets shipped, and the
backlog quietly goes stale. Dark code accumulates. The bridge closes
that loop without asking you to change how you already work.

## The flow

```
  1. Raw note dump         ->  devlead_docs/_scratchpad.md
                                         |
                                         |  triage (continuous)
                                         v
  2. Item picked for work  ->  standard plugin flow, unchanged
                                (e.g. superpowers brainstorming ->
                                 spec -> writing-plans -> plan)
                                         |
                                         |  bridge (DevLead ingests)
                                         v
  3. Actionable items      ->  devlead_docs/_intake_features.md
                                devlead_docs/_intake_bug_issues.md
                                         |
                                         |  promotion
                                         v
  4. Backlog nodes         ->  devlead_docs/_project_hierarchy.md
                                (BO / TBO / TTO)
                                         |
                                         |  normal DevLead execution
                                         v
  5. Code + commits        ->  trace back up to the originating
                                scratchpad note
```

## Worked example: using superpowers

1. In chat you say "we need an intake file for security findings".
2. Claude appends the note to `devlead_docs/_scratchpad.md`.
3. You (or Claude) run `/devlead triage`, walk the untriaged entries,
   pick this one, and classify it as a feature.
4. Claude runs the superpowers flow unchanged:
   `brainstorming -> spec -> writing-plans`. The plan lands at
   `docs/superpowers/plans/YYYY-MM-DD-security-intake.md`.
5. Claude runs
   `/devlead ingest docs/superpowers/plans/YYYY-MM-DD-security-intake.md --type features`.
   DevLead parses the plan, creates `INTF-NNNN` in
   `_intake_features.md`, and records the source path so the trace
   survives.
6. Later, promotion moves `INTF-NNNN` into `_project_hierarchy.md` as
   BO / TBO / TTO nodes. (Out of scope for this doc.)

## Zero disruption guarantee

DevLead never modifies, patches, wraps, or hooks into another plugin.
Superpowers (and every other plugin you install) stays exactly as
shipped. The ingest step is always downstream: it runs AFTER the
plugin has finished its normal work. If you uninstall DevLead tomorrow,
every other plugin keeps working exactly as it did before.

## Trace-back guarantee

Every intake entry records the source file it came from. Every
promoted TTO records the intake ID it came from. Every commit that
touches a file can be traced both directions:

- up:   commit -> TTO -> TBO -> BO -> Phase -> Vision
- down: scratchpad note -> intake entry -> TTO -> commit

This bi-directional trace is what prevents dark code from
accumulating.

## Commands

| Command | What it does |
|---|---|
| `/devlead scratchpad <title>` | Append a raw note to `_scratchpad.md` |
| `/devlead triage`             | Walk untriaged scratchpad entries     |
| `/devlead ingest <path>`      | Ingest a plugin output file           |
| `/devlead intake`             | List current intake entries           |

## Current limitations (v1)

- Ingest is Claude-driven, not automatic. Hook-based auto-ingest is a
  week-2 feature.
- Intake -> hierarchy promotion is a manual step. Day-4 work.
- Dark-code detection is principle-only today. Warn-mode lands in v1,
  optional block-mode in v1.1.
