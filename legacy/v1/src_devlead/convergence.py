"""Weighted convergence engine for DevLead.

Computes business convergence as weighted sums rolling up from
Story -> TBO -> BO -> Phase.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devlead.workbook import BO, TBO


def story_convergence(status: str) -> float:
    """Binary: 1.0 if DONE, 0.0 otherwise."""
    return 1.0 if "DONE" in status.upper() else 0.0


def tbo_convergence(tbo: TBO) -> float:
    """Weighted sum of story completion within a TBO. Returns 0-100."""
    if not tbo.stories:
        return 0.0
    total = sum(s.weight * story_convergence(s.status) for s in tbo.stories)
    weight_sum = sum(s.weight for s in tbo.stories)
    return (total / weight_sum * 100) if weight_sum > 0 else 0.0


def bo_convergence(bo: BO) -> float:
    """Weighted sum of TBO convergence within a BO. Returns 0-100."""
    if not bo.tbos:
        return 0.0
    total = sum(t.weight * tbo_convergence(t) for t in bo.tbos)
    weight_sum = sum(t.weight for t in bo.tbos)
    return (total / weight_sum) if weight_sum > 0 else 0.0


def phase_convergence(bos: list[BO]) -> float:
    """Weighted sum of BO convergence across a phase. Returns 0-100."""
    if not bos:
        return 0.0
    total = sum(b.weight * bo_convergence(b) for b in bos)
    weight_sum = sum(b.weight for b in bos)
    return (total / weight_sum) if weight_sum > 0 else 0.0


def coverage_score(bo: BO) -> float:
    """What % of BO weight has TBOs defined. Returns 0-100."""
    if not bo.tbos:
        return 0.0
    return min(sum(t.weight for t in bo.tbos), 100)


def traceability_score(total_tasks: int, traced_tasks: int) -> float:
    """% of tasks that trace to a BO. Returns 0-100."""
    if total_tasks == 0:
        return 100.0
    return traced_tasks / total_tasks * 100
