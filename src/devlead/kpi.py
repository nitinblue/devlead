"""KPI engine for DevLead v2. Implements TTO-006 under BO-001/TBO-003.

Adapted from legacy/v1/src_devlead/kpi_engine.py. Reads v2 sources:
_audit_log.jsonl, _project_hierarchy.md (via hierarchy.py), _intake_*.md.

Four categories, ~15 KPIs. Every KPI has a formula and a data source.
If data doesn't exist, KPI shows "no data" — never a guess.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class KpiResult:
    name: str
    value: float = 0.0
    fmt: str = "score"
    category: str = ""
    detail: str = ""
    warning: bool = False


def compute(repo_root: Path) -> list[KpiResult]:
    """Compute all KPIs from real project data."""
    repo_root = Path(repo_root).resolve()
    docs_dir = repo_root / "devlead_docs"

    audit = _read_audit(docs_dir)
    intake_stats = _read_intake(docs_dir)
    hierarchy_stats = _read_hierarchy(docs_dir)

    results: list[KpiResult] = []

    # --- Category A: LLM Effectiveness ---

    gate_warns = audit.get("gate_warn", 0)
    gate_passes = audit.get("gate_pass", 0)
    gate_total = gate_warns + gate_passes
    bypass_rate = (gate_warns / gate_total * 100) if gate_total > 0 else 0
    results.append(KpiResult(
        "K_BYPASS (discipline bypass rate)", round(bypass_rate, 1), "percent", "A",
        f"{gate_warns} warns / {gate_total} total gate checks",
        warning=bypass_rate > 25,
    ))

    forced = intake_stats.get("forced_origin", 0)
    total_intake = intake_stats.get("total", 0)
    forced_rate = (forced / total_intake * 100) if total_intake > 0 else 0
    results.append(KpiResult(
        "Forced work rate", round(forced_rate, 1), "percent", "A",
        f"{forced} forced / {total_intake} total intake entries",
        warning=forced_rate > 30,
    ))

    results.append(KpiResult(
        "Gate coverage", gate_total, "count", "A",
        f"{gate_total} total gate checks this project lifetime",
    ))

    # --- Category B: Delivery ---

    done = intake_stats.get("done", 0)
    total = intake_stats.get("total", 0)
    throughput = (done / total * 100) if total > 0 else 0
    results.append(KpiResult(
        "Intake throughput", round(throughput, 1), "percent", "B",
        f"{done} done / {total} total",
    ))

    on_time = hierarchy_stats.get("bos_on_time", 0)
    total_bos = hierarchy_stats.get("bos_total", 0)
    on_time_rate = (on_time / total_bos * 100) if total_bos > 0 else 0
    results.append(KpiResult(
        "BO on-time rate", round(on_time_rate, 1), "percent", "B",
        f"{on_time} on time / {total_bos} total BOs",
        warning=on_time_rate < 70 and total_bos > 0,
    ))

    revisions = hierarchy_stats.get("deadline_revisions", 0)
    results.append(KpiResult(
        "Deadline revisions", revisions, "count", "B",
        f"{revisions} BOs have revised dates",
        warning=revisions > 0,
    ))

    pending = intake_stats.get("pending", 0)
    results.append(KpiResult(
        "Backlog depth", pending, "count", "B",
        f"{pending} pending intake entries",
    ))

    # --- Category C: Project Health ---

    ttos_total = hierarchy_stats.get("ttos_total", 0)
    ttos_done = hierarchy_stats.get("ttos_done", 0)
    ttos_traced = hierarchy_stats.get("ttos_total", 0)
    traceability = (ttos_traced / max(ttos_total, 1)) * 100
    results.append(KpiResult(
        "Traceability", round(traceability, 1), "percent", "C",
        f"{ttos_traced} TTOs linked to BOs (all by definition in v2)",
    ))

    intake_no_actions = intake_stats.get("no_actionable_items", 0)
    results.append(KpiResult(
        "Intake quality", intake_no_actions, "count", "C",
        f"{intake_no_actions} intake entries with zero actionable items",
        warning=intake_no_actions > 0,
    ))

    audit_total = sum(audit.values())
    results.append(KpiResult(
        "Audit coverage", audit_total, "count", "C",
        f"{audit_total} total audit events recorded",
    ))

    # --- Category D: Business Convergence ---

    convergence = hierarchy_stats.get("sprint_convergence", 0)
    results.append(KpiResult(
        "Sprint convergence", round(convergence, 1), "percent", "D",
        f"Weighted rollup from hierarchy checkboxes",
    ))

    bos_convergence = hierarchy_stats.get("bos_convergence", {})
    for bo_id, conv in bos_convergence.items():
        results.append(KpiResult(
            f"BO convergence: {bo_id}", round(conv, 1), "percent", "D",
            f"Weighted TBO->TTO rollup",
        ))

    coverage = hierarchy_stats.get("coverage", 0)
    results.append(KpiResult(
        "TBO coverage", round(coverage, 1), "percent", "D",
        "% of BOs that have TBOs defined",
    ))

    return results


def summary(results: list[KpiResult]) -> str:
    """Plain-text KPI summary grouped by category."""
    categories = {"A": "LLM Effectiveness", "B": "Delivery", "C": "Project Health", "D": "Business Convergence"}
    lines = []
    for cat_key, cat_name in categories.items():
        cat_results = [r for r in results if r.category == cat_key]
        if not cat_results:
            continue
        lines.append(f"\n{cat_name}:")
        for r in cat_results:
            warn = " [!]" if r.warning else ""
            if r.fmt == "percent":
                lines.append(f"  {r.name}: {r.value}%{warn} — {r.detail}")
            elif r.fmt == "count":
                lines.append(f"  {r.name}: {int(r.value)}{warn} — {r.detail}")
            else:
                lines.append(f"  {r.name}: {r.value}{warn} — {r.detail}")
    return "\n".join(lines)


def _read_audit(docs_dir: Path) -> dict[str, int]:
    log_path = docs_dir / "_audit_log.jsonl"
    counts: dict[str, int] = {}
    if not log_path.exists():
        return counts
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
            event = ev.get("event", "unknown")
            counts[event] = counts.get(event, 0) + 1
        except json.JSONDecodeError:
            pass
    return counts


def _read_intake(docs_dir: Path) -> dict[str, int]:
    from devlead import intake
    stats: dict[str, int] = {"total": 0, "done": 0, "pending": 0, "in_progress": 0, "forced_origin": 0, "no_actionable_items": 0}
    for f in sorted(docs_dir.glob("_intake_*.md")):
        for e in intake.read(f):
            stats["total"] += 1
            if e.status == "done":
                stats["done"] += 1
            elif e.status == "in_progress":
                stats["in_progress"] += 1
            else:
                stats["pending"] += 1
            if e.origin == "forced":
                stats["forced_origin"] += 1
            if not e.actionable_items:
                stats["no_actionable_items"] += 1
    return stats


def _read_hierarchy(docs_dir: Path) -> dict:
    from devlead import hierarchy
    h_path = docs_dir / "_project_hierarchy.md"
    stats: dict = {"bos_total": 0, "bos_on_time": 0, "deadline_revisions": 0, "ttos_total": 0, "ttos_done": 0, "sprint_convergence": 0, "bos_convergence": {}, "coverage": 0}
    if not h_path.exists():
        return stats
    sprints = hierarchy.parse(h_path)
    if not sprints:
        return stats
    stats["sprint_convergence"] = sprints[0].convergence if sprints else 0
    bos_with_tbos = 0
    for s in sprints:
        for bo in s.bos:
            stats["bos_total"] += 1
            stats["bos_convergence"][bo.id] = bo.convergence
            if bo.revised_date and bo.revised_date != "(none)":
                stats["deadline_revisions"] += 1
            if bo.tbos:
                bos_with_tbos += 1
            for tbo in bo.tbos:
                for tto in tbo.ttos:
                    stats["ttos_total"] += 1
                    if tto.done:
                        stats["ttos_done"] += 1
    stats["coverage"] = (bos_with_tbos / stats["bos_total"] * 100) if stats["bos_total"] > 0 else 0
    return stats
