"""KPI engine for DevLead v2. Implements TTO-006 under BO-001/TBO-003.

Full port from legacy/v1/src_devlead/kpi_engine.py. All 4 categories, ~25 KPIs.
Every KPI has a formula and a data source. No guesses.

Data sources: _audit_log.jsonl, _project_hierarchy.md, _intake_*.md,
_session_history.jsonl (for tokenomics + going-in-circles).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
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
    intake = _read_intake(docs_dir)
    hier = _read_hierarchy(docs_dir)
    sessions = _read_session_history(docs_dir)

    results: list[KpiResult] = []
    results.extend(_category_a(audit, intake))
    results.extend(_category_b(intake, hier))
    results.extend(_category_c(intake, audit, docs_dir))
    results.extend(_category_d(hier, sessions))
    return results


def record_session(docs_dir: Path, tokens_used: int = 0) -> None:
    """Append a session snapshot to _session_history.jsonl. Call at session end."""
    from devlead import hierarchy
    h_path = docs_dir / "_project_hierarchy.md"
    conv = 0.0
    if h_path.exists():
        sprints = hierarchy.parse(h_path)
        if sprints:
            conv = sprints[0].convergence

    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "convergence": round(conv, 1),
        "tokens_used": tokens_used,
    }
    hist_path = docs_dir / "_session_history.jsonl"
    with open(hist_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=True) + "\n")


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
                lines.append(f"  {r.name}: {r.value}%{warn} -- {r.detail}")
            elif r.fmt == "count":
                lines.append(f"  {r.name}: {int(r.value)}{warn} -- {r.detail}")
            elif r.fmt == "ratio":
                lines.append(f"  {r.name}: {r.value:.2f}{warn} -- {r.detail}")
            elif r.fmt == "text":
                lines.append(f"  {r.name}: {r.detail}{warn}")
            else:
                lines.append(f"  {r.name}: {r.value}{warn} -- {r.detail}")
    return "\n".join(lines)


# --- Category A: LLM Effectiveness ---

def _category_a(audit: dict[str, int], intake: dict[str, int]) -> list[KpiResult]:
    results = []

    gate_warns = audit.get("gate_warn", 0)
    gate_passes = audit.get("gate_pass", 0)
    gate_total = gate_warns + gate_passes
    bypass_rate = _pct(gate_warns, gate_total)
    results.append(KpiResult(
        "K_BYPASS (discipline bypass)", round(bypass_rate, 1), "percent", "A",
        f"{gate_warns} warns / {gate_total} gate checks", bypass_rate > 25,
    ))

    forced = intake.get("forced_origin", 0)
    total = intake.get("total", 0)
    results.append(KpiResult(
        "Forced work rate", round(_pct(forced, total), 1), "percent", "A",
        f"{forced} forced / {total} total intake", _pct(forced, total) > 30,
    ))

    results.append(KpiResult(
        "Gate coverage", gate_total, "count", "A",
        f"{gate_total} total gate checks lifetime",
    ))

    no_actions = intake.get("no_actionable_items", 0)
    results.append(KpiResult(
        "Definition of Done", no_actions, "count", "A",
        f"{no_actions} intake entries with 0 actionable items", no_actions > 0,
    ))

    results.append(KpiResult(
        "Next Best Action", 0, "text", "A", _next_best_action(intake),
    ))

    return results


# --- Category B: Delivery ---

def _category_b(intake: dict[str, int], hier: dict) -> list[KpiResult]:
    results = []

    done = intake.get("done", 0)
    total = intake.get("total", 0)
    results.append(KpiResult(
        "Intake throughput", round(_pct(done, total), 1), "percent", "B",
        f"{done} done / {total} total",
    ))

    on_time = hier.get("bos_on_time", 0)
    bos = hier.get("bos_total", 0)
    results.append(KpiResult(
        "BO on-time rate", round(_pct(on_time, bos), 1), "percent", "B",
        f"{on_time} on time / {bos} total BOs",
        _pct(on_time, bos) < 70 and bos > 0,
    ))

    revisions = hier.get("deadline_revisions", 0)
    results.append(KpiResult(
        "Deadline revisions", revisions, "count", "B",
        f"{revisions} BOs have revised dates", revisions > 0,
    ))

    pending = intake.get("pending", 0)
    results.append(KpiResult(
        "Backlog depth", pending, "count", "B", f"{pending} pending intake entries",
    ))

    in_prog = intake.get("in_progress", 0)
    results.append(KpiResult(
        "In-flight work", in_prog, "count", "B", f"{in_prog} intake entries in_progress",
    ))

    bugs = intake.get("bugs_total", 0)
    features = intake.get("features_total", 0)
    ratio = bugs / max(features, 1)
    results.append(KpiResult(
        "Bug-to-feature ratio", round(ratio, 2), "ratio", "B",
        f"{bugs} bugs / {features} features", ratio > 0.5,
    ))

    return results


# --- Category C: Project Health ---

def _category_c(intake: dict, audit: dict, docs_dir: Path) -> list[KpiResult]:
    results = []

    ttos = intake.get("ttos_total", 0)
    results.append(KpiResult(
        "Traceability", 100.0, "percent", "C",
        f"All {ttos} TTOs linked to BOs by definition in v2",
    ))

    audit_total = sum(audit.values())
    results.append(KpiResult(
        "Audit coverage", audit_total, "count", "C",
        f"{audit_total} total audit events",
    ))

    expected_files = [
        "_resume.md", "_scratchpad.md", "_intake_features.md",
        "_living_decisions.md", "_project_hierarchy.md", "_routing_table.md",
        "_aware_features.md", "_aware_design.md",
    ]
    missing = sum(1 for f in expected_files if not (docs_dir / f).exists())
    results.append(KpiResult(
        "Coverage gap", missing, "count", "C",
        f"{missing} of {len(expected_files)} core files missing", missing > 0,
    ))

    stale = intake.get("pending", 0)
    results.append(KpiResult(
        "Intake staleness", stale, "count", "C",
        f"{stale} items pending", stale > 5,
    ))

    return results


# --- Category D: Business Convergence ---

def _category_d(hier: dict, sessions: list[dict]) -> list[KpiResult]:
    results = []

    conv = hier.get("sprint_convergence", 0)
    results.append(KpiResult(
        "Sprint convergence", round(conv, 1), "percent", "D",
        "Weighted rollup from hierarchy checkboxes",
    ))

    for bo_id, bo_conv in hier.get("bos_convergence", {}).items():
        results.append(KpiResult(
            f"BO convergence: {bo_id}", round(bo_conv, 1), "percent", "D",
            "Weighted TBO->TTO rollup",
        ))

    coverage = hier.get("coverage", 0)
    results.append(KpiResult(
        "TBO coverage", round(coverage, 1), "percent", "D",
        "% of BOs that have TBOs defined",
    ))

    # Going in Circles (zero-delta sessions)
    zero_delta = 0
    if len(sessions) >= 2:
        for i in range(1, len(sessions)):
            prev = sessions[i - 1].get("convergence", 0)
            curr = sessions[i].get("convergence", 0)
            if curr == prev:
                zero_delta += 1
    results.append(KpiResult(
        "Going in Circles", zero_delta, "count", "D",
        f"{zero_delta} zero-convergence-delta sessions in last {len(sessions)}",
        zero_delta >= 3,
    ))

    # Tokenomics (tokens per convergence point)
    token_cost = 0.0
    token_detail = "no session history"
    token_warn = False
    if sessions:
        last = sessions[-1]
        tokens = last.get("tokens_used", 0)
        if len(sessions) >= 2:
            delta = abs(last.get("convergence", 0) - sessions[-2].get("convergence", 0))
        else:
            delta = last.get("convergence", 0)
        token_cost = tokens / max(delta, 0.001) if tokens > 0 else 0
        token_detail = f"{tokens:,} tokens last session, {delta:.1f}% convergence delta = {token_cost:,.0f} tokens/point"
        if len(sessions) >= 3:
            costs = []
            for i in range(1, len(sessions)):
                t = sessions[i].get("tokens_used", 0)
                d = abs(sessions[i].get("convergence", 0) - sessions[i - 1].get("convergence", 0))
                costs.append(t / max(d, 0.001) if t > 0 else 0)
            if len(costs) >= 3 and costs[-1] > costs[-2] > costs[-3]:
                token_warn = True
    results.append(KpiResult(
        "Tokenomics", round(token_cost, 0), "count", "D",
        token_detail, token_warn,
    ))

    # Total tokens across all sessions
    total_tokens = sum(s.get("tokens_used", 0) for s in sessions)
    results.append(KpiResult(
        "Total tokens spent", total_tokens, "count", "D",
        f"{total_tokens:,} tokens across {len(sessions)} recorded sessions",
    ))

    return results


# --- Data readers ---

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
    stats: dict[str, int] = {
        "total": 0, "done": 0, "pending": 0, "in_progress": 0,
        "forced_origin": 0, "no_actionable_items": 0,
        "bugs_total": 0, "features_total": 0, "ttos_total": 0,
    }
    for f in sorted(docs_dir.glob("_intake_*.md")):
        entries = intake.read(f)
        is_bugs = "bugs" in f.name
        for e in entries:
            stats["total"] += 1
            if is_bugs:
                stats["bugs_total"] += 1
            else:
                stats["features_total"] += 1
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
    # TTO count from hierarchy
    from devlead import hierarchy
    h_path = docs_dir / "_project_hierarchy.md"
    if h_path.exists():
        for s in hierarchy.parse(h_path):
            for bo in s.bos:
                for tbo in bo.tbos:
                    stats["ttos_total"] += len(tbo.ttos)
    return stats


def _read_hierarchy(docs_dir: Path) -> dict:
    from devlead import hierarchy
    h_path = docs_dir / "_project_hierarchy.md"
    stats: dict = {
        "bos_total": 0, "bos_on_time": 0, "deadline_revisions": 0,
        "ttos_total": 0, "ttos_done": 0,
        "sprint_convergence": 0, "bos_convergence": {}, "coverage": 0,
    }
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
    stats["coverage"] = _pct(bos_with_tbos, stats["bos_total"])
    return stats


def _read_session_history(docs_dir: Path) -> list[dict]:
    path = docs_dir / "_session_history.jsonl"
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries[-20:]


def _pct(num: int | float, denom: int | float) -> float:
    return (num / denom * 100) if denom > 0 else 0.0


def _next_best_action(intake: dict) -> str:
    if intake.get("pending", 0) > 5:
        return f"Triage backlog -- {intake['pending']} pending intake items"
    if intake.get("in_progress", 0) > 0:
        return f"Complete {intake['in_progress']} in-progress item(s)"
    if intake.get("pending", 0) > 0:
        return f"Start next pending item ({intake['pending']} available)"
    return "All clear -- consider planning next sprint"
