"""Parse _project_hierarchy.md into a BO/TBO/TTO tree and compute convergence.

Ported from legacy/v1/src_devlead/convergence.py (weighted rollups) adapted
to read from v2's markdown checkbox format instead of v1's workbook objects.

Implements TTO-005 under BO-001/TBO-002.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TTO:
    id: str
    name: str
    weight: int
    done: bool
    ttype: str = "functional"


@dataclass
class TBO:
    id: str
    name: str
    weight: int
    ttos: list[TTO] = field(default_factory=list)

    @property
    def convergence(self) -> float:
        if not self.ttos:
            return 0.0
        total = sum(t.weight * (1.0 if t.done else 0.0) for t in self.ttos)
        weight_sum = sum(t.weight for t in self.ttos)
        return (total / weight_sum * 100) if weight_sum > 0 else 0.0


@dataclass
class BO:
    id: str
    name: str
    weight: int
    acceptance: str = ""
    start_date: str = ""
    end_date: str = ""
    actual_date: str = "(pending)"
    revised_date: str = "(none)"
    revision_justification: str = "(none)"
    tbos: list[TBO] = field(default_factory=list)

    @property
    def convergence(self) -> float:
        if not self.tbos:
            return 0.0
        total = sum(t.weight * t.convergence for t in self.tbos)
        weight_sum = sum(t.weight for t in self.tbos)
        return (total / weight_sum) if weight_sum > 0 else 0.0


@dataclass
class Sprint:
    name: str
    bos: list[BO] = field(default_factory=list)

    @property
    def convergence(self) -> float:
        if not self.bos:
            return 0.0
        total = sum(b.weight * b.convergence for b in self.bos)
        weight_sum = sum(b.weight for b in self.bos)
        return (total / weight_sum) if weight_sum > 0 else 0.0


_BO_RE = re.compile(r"^### (BO-\d+):\s*(.+?)\s*\(weight:\s*(\d+)\)")
_TBO_RE = re.compile(r"^#### (TBO-\d+):\s*(.+?)\s*\(weight:\s*(\d+)\)")
_TTO_RE = re.compile(
    r"^- \[([ xX])\] (TTO-\d+):\s*(.*?)\(weight:\s*(\d+)\)\s*\[([^\]]+)"
)
_FIELD_RE = re.compile(r"^- \*\*(\w[\w_]*):\*\*\s*(.*)")
_SPRINT_RE = re.compile(r"^## Sprint \d+\s*[-—]\s*(.+)")


def parse(hierarchy_path: Path) -> list[Sprint]:
    """Parse _project_hierarchy.md into a list of Sprints."""
    text = Path(hierarchy_path).read_text(encoding="utf-8")
    sprints: list[Sprint] = []
    current_sprint: Sprint | None = None
    current_bo: BO | None = None
    current_tbo: TBO | None = None

    for line in text.splitlines():
        sm = _SPRINT_RE.match(line)
        if sm:
            current_sprint = Sprint(name=sm.group(1).strip())
            sprints.append(current_sprint)
            current_bo = None
            current_tbo = None
            continue

        bm = _BO_RE.match(line)
        if bm and current_sprint is not None:
            current_bo = BO(
                id=bm.group(1), name=bm.group(2).strip(),
                weight=int(bm.group(3)),
            )
            current_sprint.bos.append(current_bo)
            current_tbo = None
            continue

        if current_bo is not None:
            fm = _FIELD_RE.match(line)
            if fm:
                key, val = fm.group(1), fm.group(2).strip()
                key_lower = key.lower().replace(" ", "_")
                if hasattr(current_bo, key_lower):
                    setattr(current_bo, key_lower, val)
                continue

        tbm = _TBO_RE.match(line)
        if tbm and current_bo is not None:
            current_tbo = TBO(
                id=tbm.group(1), name=tbm.group(2).strip(),
                weight=int(tbm.group(3)),
            )
            current_bo.tbos.append(current_tbo)
            continue

        ttm = _TTO_RE.match(line)
        if ttm and current_tbo is not None:
            current_tbo.ttos.append(TTO(
                id=ttm.group(2), name=ttm.group(3).strip(),
                weight=int(ttm.group(4)),
                done=ttm.group(1).strip().lower() == "x",
                ttype=ttm.group(5).strip(),
            ))

    return sprints


def summary(sprints: list[Sprint]) -> str:
    """Plain-text convergence summary."""
    lines = []
    for s in sprints:
        lines.append(f"Sprint: {s.name} — {s.convergence:.1f}% converged")
        for bo in s.bos:
            lines.append(f"  {bo.id}: {bo.name} — {bo.convergence:.1f}%")
            if bo.end_date and bo.end_date != "(pending)":
                lines.append(f"    deadline: {bo.end_date}")
            for tbo in bo.tbos:
                done = sum(1 for t in tbo.ttos if t.done)
                total = len(tbo.ttos)
                lines.append(
                    f"    {tbo.id}: {tbo.name} — {tbo.convergence:.1f}% ({done}/{total} TTOs)"
                )
    return "\n".join(lines)
