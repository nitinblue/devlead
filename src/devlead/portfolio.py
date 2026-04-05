"""Multi-project portfolio — workspace management and cross-project KPIs."""

import json
from datetime import date
from pathlib import Path

from devlead.doc_parser import get_builtin_vars
from devlead.kpi_engine import KpiResult


WORKSPACE_FILE = "workspace.json"


def _ensure_workspace(workspace_dir: Path) -> None:
    """Create workspace directory if needed."""
    workspace_dir.mkdir(parents=True, exist_ok=True)


def load_workspace(workspace_dir: Path) -> dict:
    """Load workspace config. Returns empty workspace if not found."""
    ws_file = workspace_dir / WORKSPACE_FILE
    if ws_file.exists():
        return json.loads(ws_file.read_text())
    return {"projects": []}


def save_workspace(workspace_dir: Path, workspace: dict) -> None:
    """Save workspace config."""
    _ensure_workspace(workspace_dir)
    ws_file = workspace_dir / WORKSPACE_FILE
    ws_file.write_text(json.dumps(workspace, indent=2))


def add_project(workspace_dir: Path, path: str, name: str) -> None:
    """Register a project in the workspace."""
    ws = load_workspace(workspace_dir)

    # Check for duplicate
    for p in ws["projects"]:
        if p["name"] == name:
            return  # Already registered

    ws["projects"].append({"name": name, "path": path})
    save_workspace(workspace_dir, ws)


def remove_project(workspace_dir: Path, name: str) -> None:
    """Unregister a project from the workspace."""
    ws = load_workspace(workspace_dir)
    ws["projects"] = [p for p in ws["projects"] if p["name"] != name]
    save_workspace(workspace_dir, ws)


def list_projects(workspace_dir: Path) -> list[dict]:
    """List registered projects."""
    ws = load_workspace(workspace_dir)
    return ws["projects"]


def compute_portfolio_kpis(workspace_dir: Path) -> list[KpiResult]:
    """Compute cross-project KPIs (KPIs 24-30)."""
    ws = load_workspace(workspace_dir)
    projects = ws["projects"]
    results = []

    if not projects:
        results.append(KpiResult(
            name="Portfolio Convergence",
            value=0,
            format="percent",
            category="PORTFOLIO",
            detail="No projects registered",
        ))
        return results

    # Gather per-project vars
    project_vars = []
    for proj in projects:
        docs_dir = Path(proj["path"]) / "claude_docs"
        if docs_dir.exists():
            vars = get_builtin_vars(docs_dir)
            project_vars.append({"name": proj["name"], "vars": vars})

    if not project_vars:
        results.append(KpiResult(
            name="Portfolio Convergence",
            value=0,
            format="percent",
            category="PORTFOLIO",
            detail="No project docs found",
        ))
        return results

    # KPI 24: Portfolio Convergence (weighted average)
    total_stories = sum(pv["vars"].get("stories_total", 0) for pv in project_vars)
    total_done = sum(pv["vars"].get("stories_done", 0) for pv in project_vars)
    portfolio_conv = (total_done / total_stories * 100) if total_stories > 0 else 0
    results.append(KpiResult(
        name="Portfolio Convergence",
        value=round(portfolio_conv, 1),
        format="percent",
        category="PORTFOLIO",
        detail=f"{total_done}/{total_stories} stories across {len(project_vars)} projects",
    ))

    # KPI 25: Cross-Project Blockers
    total_blocked = sum(pv["vars"].get("tasks_blocked", 0) for pv in project_vars)
    results.append(KpiResult(
        name="Cross-Project Blockers",
        value=total_blocked,
        format="count",
        category="PORTFOLIO",
        detail=f"{total_blocked} blocked tasks across projects",
        warning=total_blocked > 3,
    ))

    # KPI 27: Weakest Link
    worst_name = ""
    worst_conv = 100
    for pv in project_vars:
        conv = pv["vars"].get("convergence", 0)
        if conv < worst_conv:
            worst_conv = conv
            worst_name = pv["name"]
    results.append(KpiResult(
        name="Weakest Link",
        value=worst_conv,
        format="score",
        category="PORTFOLIO",
        detail=f"{worst_name} ({worst_conv:.0f}% convergence)",
    ))

    # KPI 28: Portfolio Velocity
    total_velocity = sum(pv["vars"].get("stories_done", 0) for pv in project_vars)
    results.append(KpiResult(
        name="Portfolio Velocity",
        value=total_velocity,
        format="count",
        category="PORTFOLIO",
        detail=f"{total_velocity} stories completed across projects",
    ))

    # KPI 26, 29, 30 require session history — placeholders
    results.append(KpiResult(
        name="Time Allocation Balance",
        value=0,
        format="score",
        category="PORTFOLIO",
        detail="Requires session history",
    ))
    results.append(KpiResult(
        name="Context Switch Cost",
        value=0,
        format="count",
        category="PORTFOLIO",
        detail="Requires session history",
    ))
    results.append(KpiResult(
        name="Collab Response Time",
        value=0,
        format="days",
        category="PORTFOLIO",
        detail="Requires collab channel",
    ))

    return results


def format_portfolio_dashboard(
    projects: list[dict], results: list[KpiResult]
) -> str:
    """Format portfolio dashboard for terminal."""
    lines = []
    sep = "=" * 72
    lines.append(sep)
    lines.append(f"  DevLead Portfolio — {date.today()}")
    lines.append(sep)

    if projects:
        lines.append("")
        lines.append(f"  {'PROJECT':<20} | {'Convergence':>12} | {'Tasks':>8}")
        lines.append("  " + "-" * 50)
        for proj in projects:
            docs_dir = Path(proj["path"]) / "claude_docs"
            if docs_dir.exists():
                vars = get_builtin_vars(docs_dir)
                conv = vars.get("convergence", 0)
                total = vars.get("tasks_total", 0)
                lines.append(
                    f"  {proj['name']:<20} | {conv:>10.0f}% | {total:>8}"
                )
            else:
                lines.append(f"  {proj['name']:<20} | {'N/A':>12} | {'N/A':>8}")

    lines.append("")
    lines.append("  CROSS-PROJECT")
    lines.append("  " + "-" * 50)
    for r in results:
        if r.format == "percent":
            val = f"{r.value:.0f}%"
        elif r.format == "count":
            val = f"{r.value:.0f}"
        elif r.format == "days":
            val = f"{r.value:.1f}d"
        else:
            val = f"{r.value:.0f}/100"
        detail = f" | {r.detail}" if r.detail else ""
        lines.append(f"  {r.name:<22} | {val:<12}{detail}")

    lines.append("")
    lines.append(sep)
    return "\n".join(lines)
