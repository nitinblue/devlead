# Standing Instructions

> Type: LIVING
> Last updated: {date}

## Rules

1. **`devlead_docs/` is the system of record.** All project state lives here.
2. **Always orient before executing.** Read status, tasks, intake first.
3. **Update docs at session end.** Status, tasks, intake — keep them current.

## Model Ownership — "I won't fly in the dark"

4. **The model owns the business-to-technical mapping.** Before recommending work, the model must be able to trace it to a Business Objective. If it can't, it says "I won't fly in the dark" and explains what's missing.

5. **Three confidence levels:**
    - **"I own this"** — Vision + frozen BOs + TBO decomposition exists. Report convergence, recommend work.
    - **"I can see the runway"** — BOs exist but TBOs not decomposed. Can do requested work, proactively decompose.
    - **"I won't fly in the dark"** — No BOs defined. Must interview user or synthesize from codebase before recommending priorities.

6. **Model owns TBO decomposition after BO freeze.** Adding a TBO after freeze = scope change. Flag explicitly.

7. **At session start, read the instrument panel.** Report phase convergence, per-BO convergence, shadow ratio, and recommended next work with traceability. Use `devlead status` output.

8. **Weighted convergence is the master number.** Not task counts, not story counts. Phase convergence (0-100) tells you how close the product is to its business objectives.
