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
    # Convergence-layer fields (Phase 1, FEATURES-0014). Optional for backward
    # compat — TTOs without intent_vector are excluded from α/φ/ε calculations.
    intent_vector: dict[str, float] = field(default_factory=dict)
    verify_kind: str = "shell"  # shell | benchmark | human_signoff | lint


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
    # Convergence-layer fields (Phase 1, FEATURES-0014). Optional for backward
    # compat — BOs without metric/baseline/target fall back to "self-reported"
    # mode; convergence math degrades to legacy weighted-tasks-done.
    metric: str = ""
    baseline: float | None = None
    target: float | None = None
    metric_source: str = ""  # "manual" | "shell:<cmd>" | "url:<endpoint>"
    current: float | None = None
    tbos: list[TBO] = field(default_factory=list)

    @property
    def convergence(self) -> float:
        if not self.tbos:
            return 0.0
        total = sum(t.weight * t.convergence for t in self.tbos)
        weight_sum = sum(t.weight for t in self.tbos)
        return (total / weight_sum) if weight_sum > 0 else 0.0

    @property
    def has_metric_source(self) -> bool:
        """True if this BO can compute a real C(τ) from convergence.py.

        Requires metric, baseline, target, and metric_source all populated.
        BOs without these fall back to legacy weighted-tasks-done convergence.
        """
        return bool(
            self.metric
            and self.metric_source
            and self.baseline is not None
            and self.target is not None
        )

    @property
    def normalised_progress(self) -> float | None:
        """Per-axis normalised progress for this BO.

        Returns (current - baseline) / (target - baseline) if metric data is
        present; None otherwise. Used by convergence.compute_s().
        """
        if not self.has_metric_source or self.current is None:
            return None
        denom = (self.target or 0.0) - (self.baseline or 0.0)
        if denom == 0.0:
            return 1.0 if self.current == self.target else 0.0
        return ((self.current or 0.0) - (self.baseline or 0.0)) / denom


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


_BO_RE = re.compile(r"^### (BO-[\d.]+):\s*(.+?)\s*\(weight:\s*(\d+)\)")
_TBO_RE = re.compile(r"^#### (TBO-[\d.]+):\s*(.+?)\s*\(weight:\s*(\d+)\)")
_TTO_RE = re.compile(
    r"^- \[([ xX])\] (TTO-[\d.]+):\s*(.*?)\(weight:\s*(\d+)\)\s*\[([^\]]+)"
)
_FIELD_RE = re.compile(r"^- \*\*(\w[\w_]*):\*\*\s*(.*)")
_TTO_SUBFIELD_RE = re.compile(r"^\s+- \*\*(\w[\w_]*):\*\*\s*(.*)")
_SPRINT_RE = re.compile(r"^## Sprint \d+\s*[-—]\s*(.+)")

# BO fields that should be parsed as float (None when not parseable / missing).
_BO_FLOAT_FIELDS = {"baseline", "target", "current"}

# TTO subfield names allowed (anything else is ignored).
_TTO_KNOWN_SUBFIELDS = {"intent", "intent_vector", "verify_kind"}


def _coerce_bo_field(bo: "BO", key: str, val: str) -> None:
    """Set a BO field from a parsed `- **Key:** value` line, with type coercion."""
    if key in _BO_FLOAT_FIELDS:
        try:
            setattr(bo, key, float(val))
        except (TypeError, ValueError):
            pass  # leave default (None); silent so legacy hierarchies parse fine
        return
    if hasattr(bo, key):
        setattr(bo, key, val)


def _parse_intent_vector(val: str) -> dict[str, float]:
    """Parse an intent_vector string like 'BO-1: 0.40, BO-3: 0.05' into a dict.

    Tolerates extra whitespace and trailing commas. Silently skips malformed
    entries — partial results are better than a parser crash on legacy files.
    """
    out: dict[str, float] = {}
    for chunk in val.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            continue
        bo_id, num = chunk.split(":", 1)
        try:
            out[bo_id.strip()] = float(num.strip())
        except (TypeError, ValueError):
            continue
    return out


def parse(hierarchy_path: Path) -> list[Sprint]:
    """Parse _project_hierarchy.md into a list of Sprints."""
    text = Path(hierarchy_path).read_text(encoding="utf-8")
    sprints: list[Sprint] = []
    current_sprint: Sprint | None = None
    current_bo: BO | None = None
    current_tbo: TBO | None = None
    current_tto: TTO | None = None

    for line in text.splitlines():
        sm = _SPRINT_RE.match(line)
        if sm:
            current_sprint = Sprint(name=sm.group(1).strip())
            sprints.append(current_sprint)
            current_bo = None
            current_tbo = None
            current_tto = None
            continue

        bm = _BO_RE.match(line)
        if bm and current_sprint is not None:
            current_bo = BO(
                id=bm.group(1), name=bm.group(2).strip(),
                weight=int(bm.group(3)),
            )
            current_sprint.bos.append(current_bo)
            current_tbo = None
            current_tto = None
            continue

        # TTO subfield (indented `  - **field:** value`) attaches to the current TTO.
        # Must be checked BEFORE the top-level _FIELD_RE so the indented form wins.
        if current_tto is not None:
            tsf = _TTO_SUBFIELD_RE.match(line)
            if tsf:
                key, val = tsf.group(1).lower(), tsf.group(2).strip()
                if key in ("intent", "intent_vector"):
                    current_tto.intent_vector = _parse_intent_vector(val)
                elif key == "verify_kind":
                    current_tto.verify_kind = val
                continue

        # BO-level field (`- **Key:** value`) at top level applies to current_bo.
        if current_bo is not None:
            fm = _FIELD_RE.match(line)
            if fm:
                key, val = fm.group(1), fm.group(2).strip()
                key_lower = key.lower().replace(" ", "_")
                _coerce_bo_field(current_bo, key_lower, val)
                continue

        tbm = _TBO_RE.match(line)
        if tbm and current_bo is not None:
            current_tbo = TBO(
                id=tbm.group(1), name=tbm.group(2).strip(),
                weight=int(tbm.group(3)),
            )
            current_bo.tbos.append(current_tbo)
            current_tto = None
            continue

        ttm = _TTO_RE.match(line)
        if ttm and current_tbo is not None:
            current_tto = TTO(
                id=ttm.group(2), name=ttm.group(3).strip(),
                weight=int(ttm.group(4)),
                done=ttm.group(1).strip().lower() == "x",
                ttype=ttm.group(5).strip(),
            )
            current_tbo.ttos.append(current_tto)

    return sprints


def coverage_score(bo: BO) -> float:
    """What % of BO weight is covered by TBOs. Returns 0-100."""
    if not bo.tbos:
        return 0.0
    return min(sum(t.weight for t in bo.tbos), 100)


def tbo_coverage_score(tbo: TBO) -> float:
    """What % of TBO weight is covered by TTOs. Returns 0-100."""
    if not tbo.ttos:
        return 0.0
    return min(sum(t.weight for t in tbo.ttos), 100)


def traceability_score(sprints: list[Sprint]) -> float:
    """% of TTOs that exist in the hierarchy (all by definition in v2). Returns 0-100."""
    total = sum(1 for s in sprints for b in s.bos for t in b.tbos for tt in t.ttos)
    return 100.0 if total > 0 else 0.0


def convergence_breakdown(sprints: list[Sprint]) -> dict:
    """Full convergence breakdown for dashboard rendering."""
    result = {"sprints": []}
    for s in sprints:
        sprint_data = {"name": s.name, "convergence": s.convergence, "bos": []}
        for bo in s.bos:
            bo_data = {
                "id": bo.id, "name": bo.name, "weight": bo.weight,
                "convergence": bo.convergence, "coverage": coverage_score(bo),
                "start_date": bo.start_date, "end_date": bo.end_date,
                "actual_date": bo.actual_date, "revised_date": bo.revised_date,
                "revision_justification": bo.revision_justification,
                "tbos": [],
            }
            for tbo in bo.tbos:
                tbo_data = {
                    "id": tbo.id, "name": tbo.name, "weight": tbo.weight,
                    "convergence": tbo.convergence, "coverage": tbo_coverage_score(tbo),
                    "ttos": [],
                }
                for tto in tbo.ttos:
                    tbo_data["ttos"].append({
                        "id": tto.id, "name": tto.name, "weight": tto.weight,
                        "done": tto.done, "ttype": tto.ttype,
                    })
                bo_data["tbos"].append(tbo_data)
            sprint_data["bos"].append(bo_data)
        result["sprints"].append(sprint_data)
    return result


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
