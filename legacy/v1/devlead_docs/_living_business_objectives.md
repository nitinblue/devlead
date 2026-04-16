# Business Objectives (TBOs)

> Type: LIVING
> Last updated: 2026-04-05

## What This File Is

Tangible Business Outcomes are the ONLY unit of business progress. A TBO describes
what the end user can do now that they couldn't before. Convergence = TBOs done / TBOs total.

TBOs are an official, managed list. They are created in consultation with the user.
Stories link to TBOs. Completion means the feature is rolled out and accepted by user.
DevLead captures the actual completion date -- planned dates are set by the user.

## TBO Tracker

| ID | Objective | Linked Stories | Status | Planned | Actual | Metric |
|----|-----------|---------------|--------|---------|--------|--------|
| TBO-1 | Single-project governance works E2E | S-001, S-002, S-003, S-004, S-005, S-006, S-007, S-008, S-009, S-010, S-011, S-012, S-013, S-017 | DONE | 2026-04-05 | 2026-04-05 | User runs `devlead init` through full 7-state lifecycle, sees KPI dashboard, rollover works. Zero manual setup. |
| TBO-2 | Multi-project portfolio governance | S-014, S-015, S-016 | ACCEPTANCE | 2026-04-06 | -- | User registers 2+ projects, sees portfolio KPIs, exchanges collab messages between them. |
| TBO-3 | Available on PyPI | S-001, S-018 | DONE | 2026-04-05 | 2026-04-05 | `pip install devlead` from PyPI installs working CLI. LICENSE, README, pyproject.toml present. Package builds and uploads. |
| TBO-4 | First paying customer | (revenue stories needed) | NOT_STARTED | 2026-04-12 | -- | One confirmed Stripe payment for Pro tier ($29/yr). Requires: license API, Stripe integration, tier gating in CLI. |

## Convergence

- TBOs total: 4
- TBOs done: 2
- Convergence: 50%

## Planned vs Actual

- TBO-1: All 13 stories DONE, 288 tests pass. Ready for user acceptance. Planned today.
- TBO-2: All 3 stories DONE. Ready for user acceptance. Planned tomorrow.
- TBO-3: Compliance done. Package build + PyPI upload remaining (~1 hour). Planned today.
- TBO-4: No revenue stories exist yet. Need: license API (FEAT-019), Stripe (FEAT-018), tier gating (FEAT-010). Planned 1 week out.
