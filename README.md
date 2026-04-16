# DevLead

**Lead your development. Don't let AI wander.**

DevLead is a governance tool that installs onto an existing project and becomes the only channel between your codebase and the model. It does not migrate your code — it constrains the model.

## Status

**v2 under construction.** The product is being redesigned from scratch. v1 code is preserved untouched at `legacy/v1/` and pinned at git tag `v1-archive-2026-04-12`.

## How it works (Section 1 — locked)

1. Install onto an existing project. DevLead creates scaffolding in `devlead_docs/` and nothing else.
2. From that point on, `devlead_docs/` is the single, canonical source of truth — both for what needs to be done and what got done.
3. LLM memory is a derived view of `devlead_docs/`. Memory's content always originates from `devlead_docs/`; it is never an independent source.
4. Work originates one of two ways: user + Claude defining it together, or Claude identifying and creating the work item itself.
5. Ordering is mandatory: intake → planning → stories/tasks in `devlead_docs/` → coding → write-back. Coding only starts after the plan is materialized on disk.
6. The model cannot jump the gun. File edits and planning/discussing are both constrained to work that originates in `devlead_docs/`.

More sections coming.

## Install

Not yet. v2 has no working code. Come back later.
