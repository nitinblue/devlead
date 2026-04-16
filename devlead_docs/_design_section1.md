# DevLead Design — Section 1: Install on Existing Project

> Status: LOCKED (2026-04-12)
> Dictated by: user
> Captured by: claude
> Next section: not yet dictated

## The use case

DevLead gets installed onto an existing, big project. Not greenfield. The project already has code, structure, maybe its own docs and history. DevLead has to bolt on without disturbing any of that.

## What install does

Install creates all the scaffolding files in `devlead_docs/`. Nothing else in the project is touched.

## The source-of-truth rule (the core rule)

From the moment install completes, `devlead_docs/` is the **single, canonical source of truth**. It is used in both directions:

- **Inbound** — everything the model needs to know about what has to be done comes from `devlead_docs/`. Tasks, stories, roadmap, standing instructions, vision, business objectives — all of it lives here.
- **Outbound** — everything the model does that matters (progress, completions, new intake items, findings) gets written back into `devlead_docs/`.

There is no other system of record. No other place the model can read from or write to that counts as real.

## LLM memory — a derived view, not a peer source

LLM memory (Claude Code's auto-memory, or any equivalent memory system the model uses) is **not** a peer source of truth. It is a **derived view** of `devlead_docs/`. Every piece of content in memory originates from `devlead_docs/` content — memory is effectively a cache of the canonical store.

Practical consequences:

- The model cannot put something into memory that is not already in (or derived from) `devlead_docs/`.
- If `devlead_docs/` changes, memory gets refreshed from it.
- Memory is never authoritative on its own. If memory and `devlead_docs/` disagree, `devlead_docs/` wins.

## Work origination — two paths

Work only enters the system in one of two ways:

1. **Path A — Collaborative.** The user works with Claude to define the work. User and model talk it through, decide what it is, write it down.
2. **Path B — Autonomous.** Claude identifies a gap, bug, or need, and creates the work item itself.

Both paths end the same way: an intake item lands in `devlead_docs/`.

## Mandatory ordering

Once an intake item exists, the lifecycle is strict:

```
intake item in devlead_docs/
        ↓
    planning (Claude plans the approach)
        ↓
plan converted into stories/tasks in devlead_docs/
        ↓
    coding (Claude implements the tasks)
        ↓
results written back into devlead_docs/
```

**Coding can only begin after the plan has been materialized into stories/tasks inside `devlead_docs/`.** A plan that lives only in chat, or only in the model's head, is not permission to code. The plan must land on disk first.

## The "no jumping the gun" rule

The model must have **no way** to jump the gun. This applies to:

- **File edits.** The model cannot edit any code file without a matching open task in `devlead_docs/`.
- **Planning / discussing.** The model cannot plan or discuss work that did not originate in the loop. Any detour must first surface as a new intake item in `devlead_docs/`.
- **Completion claims.** The model cannot mark anything "done" except by updating `devlead_docs/`.
- **Memory writes.** The model cannot put content into LLM memory that did not originate from `devlead_docs/`.

## What this section does NOT yet define

- How enforcement is implemented (hooks, gates, drift detection, UI, etc.).
- What the scaffolding file structure actually is (which files exist, their formats, their contents). This is part of a later section.
- What the install command looks like.
- How the user interacts with DevLead day-to-day.
- How memory gets refreshed from `devlead_docs/` in practice.

These are all follow-on sections to be dictated by the user next.
