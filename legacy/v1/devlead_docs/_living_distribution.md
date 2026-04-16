# Distribution

> Type: LIVING
> Last updated: 2026-04-05

## What This File Is

Tracks productionization milestones -- everything needed to go from "works on my machine"
to "available product with revenue." This is the last bookend tab on the dashboard.

## Open Source Compliance

| Milestone | Status | Depends On | Notes |
|-----------|--------|------------|-------|
| LICENSE file (MIT) | DONE | -- | MIT license added |
| README.md with install + usage | DONE | -- | Install and usage docs complete |
| pyproject.toml metadata complete | DONE | -- | Classifiers, URLs, description filled in |
| MANIFEST.in for sdist | DONE | -- | Using package_data in pyproject.toml instead |

## Package Build and Upload

| Milestone | Status | Depends On | Notes |
|-----------|--------|------------|-------|
| `python -m build` produces wheel + sdist | NOT_STARTED | pyproject.toml complete | FEAT-012 |
| TestPyPI upload and install test | NOT_STARTED | Build works | Verify `pip install` from TestPyPI |
| PyPI production upload | NOT_STARTED | TestPyPI validated | `pip install devlead` works globally |
| GitHub Actions CI (test + publish) | NOT_STARTED | PyPI credentials | Automate on tag push |

## Revenue Infrastructure

| Milestone | Status | Depends On | Notes |
|-----------|--------|------------|-------|
| Tier model defined | DONE | -- | Free / $29 Pro (5 projects) / $49 Unlimited (yearly) |
| License API (validate key, check tier) | NOT_STARTED | Tier model | FEAT-019 -- stdlib HTTP only |
| Stripe integration (checkout, webhook) | NOT_STARTED | License API | Server-side; out of CLI scope |
| Tier gating in CLI (`devlead register --key`) | NOT_STARTED | License API | Free = 1 project, Pro = 5, Unlimited = no cap |

## Marketing

| Milestone | Status | Depends On | Notes |
|-----------|--------|------------|-------|
| GitHub repo public | NOT_STARTED | LICENSE, README | Currently private |
| Landing page (static site) | NOT_STARTED | Public repo | Tagline: "Lead your development. Don't let AI wander." |
| PyPI project page polished | NOT_STARTED | README quality | PyPI renders README as project page |

## Partnership and Adoption

| Milestone | Status | Depends On | Notes |
|-----------|--------|------------|-------|
| Pitch to Anthropic (Claude Code team) | NOT_STARTED | Public repo, README | DevLead reduces wasted tokens and shadow work. Puts control back to user. Could be official Claude Code governance plugin or recommended tool. Channel: github.com/anthropics/claude-code issues/discussions or DevRel outreach. |
| Claude Code plugin marketplace listing | NOT_STARTED | Anthropic pitch | If Anthropic supports a plugin/extension ecosystem, DevLead should be listed. |
| Community adoption -- 100 GitHub stars | NOT_STARTED | Public repo | First validation that developers want governance for AI coding. |
| First external contributor | NOT_STARTED | Public repo, CONTRIBUTING.md | LLM adapter contributions (Cursor, Copilot, Windsurf) are the likely first PRs. |

## Value Proposition

**For developers:** Stop AI from wandering. Every task traces to a business outcome. Shadow work is visible and accountable. You control priorities, not the model.

**For Anthropic:** DevLead reduces wasted tokens (fewer circles, fewer rewrites, no shadow work). Reduces developer frustration by enforcing articulation and prioritization BEFORE code. Better user outcomes = less churn from Claude Code.

**For teams:** Governance across multiple AI-assisted projects. Portfolio KPIs. Cross-project collaboration. Audit trail for every file write.

## Funnel

```
Discovery (GitHub, PyPI, Anthropic recommendation)
  → Install (pip install devlead) -- FREE
    → Single project governance -- FREE
      → Hit 1-project limit
        → Pro ($29/yr, 5 projects)
          → Hit 5-project limit  
            → Unlimited ($49/yr)
```

## Summary

- Distribution milestones total: 19
- Done: 5 (tier model, LICENSE, README, pyproject.toml, package_data)
- Remaining: 14
