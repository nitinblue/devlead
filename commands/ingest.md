---
description: Ingest a plugin's output plan/spec into a DevLead intake file
---

# /devlead ingest

Usage:
  `/devlead ingest <path-to-plan-or-spec-file> --into <_intake_file.md>`
  `/devlead ingest --from-scratchpad <needle> --into <_intake_file.md>`

## What this does

Takes the output of a plugin flow (e.g. `superpowers writing-plans` produces a
file under `docs/superpowers/plans/`) and files it as a new entry in the given
DevLead intake file.

- The new entry gets a fresh ID derived from the intake filename slug:
  `_intake_features.md` -> `FEATURES-NNNN`, `_intake_security.md` ->
  `SECURITY-NNNN`, `_intake_roadmap_ideas.md` -> `ROADMAP-IDEAS-NNNN`.
- The source plugin file is recorded for traceability and is NEVER modified.
- The entry follows the template at
  `devlead_docs/_intake_templates/<slug>.md` (falls back to `_default.md`
  if no slug-specific template exists).

## How Claude should run this

1. Resolve an absolute path to the plugin output file.
2. From the project root, run:

   ```
   PYTHONPATH=src python -c "from pathlib import Path; from devlead.bridge import ingest; e = ingest(Path(r'<PLAN_PATH>'), '<INTAKE_FILENAME>', Path('devlead_docs')); print(f'wrote {e.id}: {e.title}')"
   ```

   Or (preferred if on a normal shell):

   ```
   PYTHONPATH=src python -m devlead ingest <PLAN_PATH> --into <INTAKE_FILENAME>
   ```

3. Report: which intake file was updated, the new ID, the title, and how many
   actionable items were extracted.

4. If you have strong confidence on placement, pass `proposed_bo`,
   `proposed_sprint`, and `proposed_weight` kwargs via the Python snippet form
   so the entry lands pre-triaged. Otherwise leave them as defaults and let
   the user finalize at triage.

5. If the ingest was triggered from a `/devlead triage` walk of a scratchpad
   entry, also append a cross-reference line to the scratchpad entry body:
   `-> ingested as <ID>`.

## Direct scratchpad -> intake (no plugin plan needed)

For items that don't need a full plugin planning pass - small bug fixes,
one-liner feature requests, anything already well-scoped - you can promote
a scratchpad entry directly into an intake file:

```
PYTHONPATH=src python -m devlead ingest --from-scratchpad <needle> --into <_intake_file.md>
```

`<needle>` is a lowercased substring matched against both the scratchpad
entry_id (e.g. `2026-04-14-self-awareness`) and the entry title. The first
match wins.

The new intake entry records its source as `scratchpad:<entry-id>` and the
original scratchpad entry gets a cross-reference line appended to its body
(`> **Promoted:** tracked as FEATURES-0002 in _intake_features.md.`) so the
trace is bidirectional.

**If the scratchpad entry yields no actionable items**, DevLead warns. Every
intake entry must eventually map to granular TTOs; an empty entry is a signal
that the item needs refinement (or rejection) before it becomes real work.

## Multiple intake files

DevLead recognizes any file matching `_intake_*.md` in `devlead_docs/`. You
can create your own intake categories by dropping a template file into
`_intake_templates/` and a matching data file at the top of `devlead_docs/`.
Example:

```
devlead_docs/_intake_templates/security.md   (template)
devlead_docs/_intake_security.md             (data)
```

Then `/devlead ingest <plan> --into _intake_security.md` files a SECURITY-NNNN
entry that follows the security template.

## What NOT to do

- Do NOT modify the plugin's output file. It stays authoritative; the intake
  entry is a pointer.
- Do NOT promote the intake entry into `_project_hierarchy.md` here. Promotion
  is a separate step (Day 4+).
- Do NOT guess `proposed_bo` / `proposed_sprint` / `proposed_weight` without
  real context. Leave them as `(needs ...)` and let triage finalize.
