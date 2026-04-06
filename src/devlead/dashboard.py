"""HTML dashboard generator — beautiful tabbed session report.

Generates a self-contained HTML file with embedded CSS.
Tabs: Overview, Roadmap, KPIs, Session, Audit.
No JavaScript — uses CSS radio button trick for tab switching.
"""

import json
from datetime import date, datetime
from pathlib import Path

from devlead.audit import read_audit_log
from devlead.doc_parser import get_builtin_vars, parse_table, parse_file_metadata
from devlead.kpi_engine import compute_builtin_kpis, KpiResult


def generate_dashboard_html(
    project_dir: Path,
    today: date | None = None,
) -> str:
    """Generate a complete HTML dashboard for the current session."""
    if today is None:
        today = date.today()

    docs_dir = project_dir / "claude_docs"
    state_file = docs_dir / "session_state.json"
    audit_log = docs_dir / "_audit_log.jsonl"

    # Load data — all defensively, never crash on bad formats
    state = _load_state_safe(state_file)
    project_name = project_dir.name

    try:
        vars = get_builtin_vars(docs_dir, today=today)
    except Exception:
        vars = {}

    try:
        kpis = compute_builtin_kpis(vars, docs_dir=docs_dir)
    except Exception:
        kpis = []

    try:
        audit_entries = read_audit_log(audit_log)
    except Exception:
        audit_entries = []

    # Load project tables
    epics = _load_table(docs_dir / "_project_roadmap.md")
    stories = _load_table(docs_dir / "_project_stories.md")
    tasks = _load_table(docs_dir / "_project_tasks.md")
    issues = _load_table(docs_dir / "_intake_issues.md")
    features = _load_table(docs_dir / "_intake_features.md")

    # Load file metadata for all claude_docs files
    file_metas = _load_all_file_metadata(docs_dir)

    # Build tabs
    header = _section_header(project_name, today, state)

    # Load text files for business context
    status_text = _read_safe(docs_dir / "_project_status.md")
    objectives = _load_table(docs_dir / "_living_business_objectives.md")
    objectives_text = _read_safe(docs_dir / "_living_business_objectives.md")

    tab_overview = _tab_overview(vars, state, kpis, tasks, file_metas)
    tab_business = _tab_business(epics, stories, tasks, vars, kpis, status_text, objectives, objectives_text)
    tab_roadmap = _tab_roadmap(docs_dir)
    tab_kpis = _tab_kpis(kpis)
    tab_session = _tab_session(state, project_dir=project_dir)
    tab_backlog = _tab_backlog(docs_dir)
    tab_audit = _tab_audit(audit_entries)

    tab_distribution = _tab_distribution(docs_dir)

    # Load session history for trends
    from devlead.session_history import read_session_history, compute_deltas
    history_file = docs_dir / "session_history.jsonl"
    try:
        history = read_session_history(history_file)
        deltas = compute_deltas(history)
    except Exception:
        history = []
        deltas = {}

    tab_trends = _tab_trends(history, deltas)

    tabs = _build_tabs([
        ("business", "Business", tab_business),
        ("overview", "Overview", tab_overview),
        ("roadmap", "Roadmap", tab_roadmap),
        ("kpis", "KPIs", tab_kpis),
        ("trends", "Trends", tab_trends),
        ("backlog", "Backlog", tab_backlog),
        ("session", "Session", tab_session),
        ("audit", "Audit", tab_audit),
        ("distribution", "Productionize", tab_distribution),
    ])

    return _wrap_html(project_name, today, header + tabs)


def write_dashboard(
    project_dir: Path,
    today: date | None = None,
) -> Path:
    """Generate and write the dashboard HTML file."""
    if today is None:
        today = date.today()

    html = generate_dashboard_html(project_dir, today=today)

    docs_dir = project_dir / "claude_docs"
    docs_dir.mkdir(exist_ok=True)
    filename = f"dashboard_{today.isoformat()}.html"
    path = docs_dir / filename
    path.write_text(html, encoding="utf-8")
    return path


# --- Data loading ---


def _load_state_safe(state_file: Path) -> dict:
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _read_safe(path: Path) -> str:
    """Read file text safely — never crash."""
    try:
        if path.exists():
            return path.read_text()
    except Exception:
        pass
    return ""


def _load_all_file_metadata(docs_dir: Path) -> list[dict]:
    """Load metadata from all .md files in docs_dir."""
    metas = []
    if not docs_dir.exists():
        return metas
    for f in sorted(docs_dir.glob("*.md")):
        try:
            meta = parse_file_metadata(f.read_text())
            meta["filename"] = f.name
            metas.append(meta)
        except Exception:
            metas.append({"filename": f.name, "title": f.stem, "type": "?", "last_updated": "?"})
    return metas


def _load_table(path: Path) -> list[dict]:
    """Load a markdown table safely — never crash on bad format."""
    try:
        if path.exists():
            return parse_table(path.read_text())
    except Exception:
        pass
    return []


# --- Tab builder ---


def _build_tabs(tabs: list[tuple[str, str, str]]) -> str:
    """Build CSS-only tabbed interface using radio buttons."""
    inputs = ""
    labels = ""
    panels = ""

    for i, (tab_id, label, content) in enumerate(tabs):
        checked = " checked" if i == 0 else ""
        inputs += f'<input type="radio" name="tabs" id="tab-{tab_id}"{checked} class="tab-input">\n'
        labels += f'<label for="tab-{tab_id}" class="tab-label">{_esc(label)}</label>\n'
        panels += f'<div class="tab-panel" id="panel-{tab_id}">{content}</div>\n'

    return f"""
    <div class="tabs">
        {inputs}
        <div class="tab-bar">{labels}</div>
        <div class="tab-panels">{panels}</div>
    </div>
    """


# --- Header ---


def _section_header(project_name: str, today: date, state: dict) -> str:
    current_state = state.get("state", "No session")
    session_start = state.get("session_start", "")
    transitions = state.get("transitions", [])

    duration = ""
    if transitions:
        first = transitions[0].get("at", "")
        last = transitions[-1].get("at", "")
        if first and last:
            try:
                t0 = datetime.fromisoformat(first)
                t1 = datetime.fromisoformat(last)
                mins = int((t1 - t0).total_seconds() / 60)
                duration = f"{mins}m"
            except (ValueError, TypeError):
                pass

    start_display = session_start[:19].replace("T", " ") if session_start else "—"

    return f"""
    <div class="card header-card">
        <div class="header-top">
            <h1>Project Status</h1>
            <span class="project-name">{_esc(project_name)}</span>
        </div>
        <div class="header-meta">
            <span class="badge state-badge">{_esc(current_state)}</span>
            <span>{today.isoformat()}</span>
            <span>Started: {_esc(start_display)}</span>
            {"<span>Duration: " + _esc(duration) + "</span>" if duration else ""}
            <span>{len(transitions)} transitions</span>
        </div>
    </div>
    """


# --- Tab: Overview ---


def _tab_overview(vars: dict, state: dict, kpis: list = None, tasks: list = None, file_metas: list = None) -> str:
    pipeline = _pipeline_cards(vars)
    next_action = _next_action_section(kpis or [], tasks or [])
    files = _files_section(file_metas or [])
    timeline = _timeline_section(state)
    checklist = _checklist_section(state)
    scope = _scope_section(state)
    return pipeline + next_action + files + timeline + checklist + scope


def _pipeline_cards(vars: dict) -> str:
    items = [
        ("Epics", vars.get("epics_total", 0), vars.get("epics_done", 0), vars.get("epics_in_progress", 0)),
        ("Stories", vars.get("stories_total", 0), vars.get("stories_done", 0), vars.get("stories_in_progress", 0)),
        ("Tasks", vars.get("tasks_total", 0), vars.get("tasks_done", 0), vars.get("tasks_in_progress", 0)),
        ("Intake", vars.get("intake_total", 0), vars.get("intake_closed", 0), 0),
    ]
    cards = ""
    for label, total, done, in_prog in items:
        pct = int(done / total * 100) if total > 0 else 0
        color = _pct_color(pct)
        cards += f"""
        <div class="stat-card">
            <div class="stat-value" style="color: {color}">{done}<span class="stat-of">/{total}</span></div>
            <div class="stat-label">{label}</div>
            <div class="progress-bar"><div class="progress-fill" style="width: {pct}%; background: {color}"></div></div>
            <div class="stat-sub">{in_prog} in progress</div>
        </div>
        """

    blocked = vars.get("tasks_blocked", 0)
    overdue = vars.get("tasks_overdue", 0)
    convergence = vars.get("convergence", 0)

    cards += f"""
    <div class="stat-card">
        <div class="stat-value" style="color: {'#e74c3c' if blocked else '#27ae60'}">{blocked}</div>
        <div class="stat-label">Blocked</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color: {'#e74c3c' if overdue else '#27ae60'}">{overdue}</div>
        <div class="stat-label">Overdue</div>
    </div>
    <div class="stat-card">
        <div class="stat-value" style="color: {_pct_color(convergence)}">{convergence:.0f}<span class="stat-of">%</span></div>
        <div class="stat-label">Convergence</div>
    </div>
    """
    return f'<div class="section"><h2>Pipeline</h2><div class="stat-grid">{cards}</div></div>'


def _timeline_section(state: dict) -> str:
    transitions = state.get("transitions", [])
    if not transitions:
        return '<div class="section"><h2>State Timeline</h2><p class="muted">No transitions.</p></div>'

    steps = ""
    for i, t in enumerate(transitions):
        time_str = t.get("at", "?")[:19].replace("T", " ")
        to_s = t.get("to", "?")
        active = " active" if i == len(transitions) - 1 else ""
        steps += f'<div class="tl-step{active}"><div class="tl-dot"></div><div class="tl-label">{_esc(to_s)}</div><div class="tl-time">{_esc(time_str)}</div></div>'

    return f'<div class="section"><h2>State Timeline</h2><div class="timeline-h">{steps}</div></div>'


def _checklist_section(state: dict) -> str:
    checklists = state.get("checklists", {})
    if not checklists:
        return ""

    groups = ""
    for state_name, items in checklists.items():
        total = len(items)
        done = sum(1 for v in items.values() if v)
        pct = int(done / total * 100) if total else 0

        checks = ""
        for key, val in items.items():
            icon = "&#x2705;" if val else "&#x26AA;"
            checks += f'<div class="ck-item">{icon} {_esc(key)}</div>'

        groups += f"""
        <div class="ck-group">
            <div class="ck-header">
                <h3>{_esc(state_name)}</h3>
                <span class="ck-count">{done}/{total}</span>
            </div>
            <div class="progress-bar"><div class="progress-fill" style="width: {pct}%; background: {_pct_color(pct)}"></div></div>
            {checks}
        </div>
        """
    return f'<div class="section"><h2>Checklists</h2><div class="ck-grid">{groups}</div></div>'


def _scope_section(state: dict) -> str:
    scope = state.get("scope", [])
    if not scope:
        return ""
    items = "".join(f"<li>{_esc(p)}</li>" for p in scope)
    return f'<div class="section"><h2>Scope Lock</h2><ul class="scope-list">{items}</ul></div>'


def _next_action_section(kpis: list, tasks: list) -> str:
    """What to work on next — computed from KPIs and task data."""
    # Find NBA from KPIs
    nba = None
    for k in kpis:
        if hasattr(k, 'name') and k.name == "Next Best Action" and k.detail:
            nba = k.detail
            break

    # Find highest priority unblocked tasks
    actionable = []
    for t in tasks:
        status = t.get("Status", "").upper()
        if "DONE" in status or "CLOSED" in status or "COMPLETE" in status:
            continue
        priority = t.get("Priority", "P9")
        blocked = "BLOCK" in status
        actionable.append((priority, blocked, t))

    actionable.sort(key=lambda x: (x[1], x[0]))  # unblocked first, then by priority
    top_tasks = actionable[:5]

    html = ""
    if nba:
        html += f'<div class="nba-box">{_esc(nba)}</div>'

    if top_tasks:
        rows = ""
        for pri, blocked, t in top_tasks:
            s_class = _status_class(t.get("Status", ""))
            story = t.get("Story", "—")
            rows += f"""<tr>
                <td><span class="badge-xs {s_class}">{_esc(t.get("Status", ""))}</span></td>
                <td>{_esc(t.get("ID", ""))}</td>
                <td>{_esc(t.get("Task", ""))}</td>
                <td class="muted">{_esc(t.get("Priority", ""))}</td>
                <td class="muted">{_esc(story)}</td>
            </tr>"""
        html += f"""<table class="data-table"><thead><tr><th>Status</th><th>ID</th><th>Task</th><th>Priority</th><th>Story</th></tr></thead><tbody>{rows}</tbody></table>"""

    if not html:
        html = '<p class="muted">No actionable tasks.</p>'

    return f'<div class="section"><h2>What to Work On Next</h2>{html}</div>'


def _files_section(file_metas: list[dict]) -> str:
    """Show user-editable claude_docs files with metadata."""
    if not file_metas:
        return ""

    # Only show files where users contribute: intake + project (not living, not internal)
    editable_prefixes = ("_intake_", "_project_")
    editable = [m for m in file_metas if any(m.get("filename", "").startswith(p) for p in editable_prefixes)]
    if not editable:
        return ""

    rows = ""
    for m in editable:
        fname = m.get("filename", "")
        title = m.get("title", fname)
        ftype = m.get("type", "")
        updated = m.get("last_updated", "")
        type_class = "st-prog" if ftype == "PROJECT" else "st-open" if ftype == "INTAKE" else "st-default" if ftype == "LIVING" else "st-default"

        rows += f"""<tr>
            <td><span class="badge-xs {type_class}">{_esc(ftype)}</span></td>
            <td class="mono">{_esc(fname)}</td>
            <td>{_esc(title)}</td>
            <td class="muted">{_esc(updated)}</td>
        </tr>"""

    return f"""
    <div class="section">
        <h2>Project Files <span class="count">({len(editable)})</span></h2>
        <table class="data-table"><thead><tr><th>Type</th><th>File</th><th>Title</th><th>Updated</th></tr></thead><tbody>{rows}</tbody></table>
    </div>
    """


# --- Tab: Business ---


def _tab_business(epics: list[dict], stories: list[dict], tasks: list[dict], vars: dict, kpis: list, status_text: str, objectives: list[dict] = None, objectives_text: str = "") -> str:
    """Business tab — project overview from business/product POV.

    Centered on TBOs (Tangible Business Outcomes). Epic/Story/Task is technical
    and belongs in the Roadmap tab. This tab answers: are we delivering value?
    """
    html = ""

    # --- Product Vision ---
    if objectives_text:
        section = _extract_section(objectives_text, "Product Vision")
        if section and section.strip() and not section.strip().startswith("_"):
            html += f'<div class="section"><div class="vision-box">{_render_prose(section)}</div></div>'

    # --- TBO Convergence hero ---
    tbo_total = len(objectives) if objectives else 0
    tbo_done = sum(1 for o in (objectives or []) if "DONE" in o.get("Status", "").upper())
    tbo_pct = int(tbo_done / tbo_total * 100) if tbo_total > 0 else 0

    html += f"""
    <div class="section">
        <div class="convergence-hero">
            <div class="conv-number" style="color: {_pct_color(tbo_pct)}">{tbo_pct}%</div>
            <div class="conv-label">{tbo_done} of {tbo_total} business outcomes delivered</div>
        </div>
    </div>
    """

    # --- TBO Table (centerpiece) ---
    if objectives:
        rows = ""
        for obj in objectives:
            tbo_id = obj.get("ID", "").strip()
            tbo_name = obj.get("TBO", obj.get("Objective", "")).strip()
            tbo_status = obj.get("Status", "").strip()
            tbo_stories_ref = obj.get("Stories", "").strip()
            tbo_owner = obj.get("Owner", "").strip()
            tbo_due = obj.get("Due", "").strip()
            tbo_priority = obj.get("Priority", "").strip()
            tbo_risks = obj.get("Risks", "").strip()
            tbo_blockers = obj.get("Blockers", "").strip()

            s_class = _status_class(tbo_status)

            # Count linked stories done
            linked_ids = [s.strip() for s in tbo_stories_ref.replace(",", " ").split() if s.strip().startswith("S-")]
            linked_done = sum(
                1 for sid in linked_ids
                for s in stories
                if s.get("ID", "").strip() == sid and "DONE" in s.get("Status", "").upper()
            )
            linked_total = len(linked_ids)
            story_pct = int(linked_done / linked_total * 100) if linked_total > 0 else 0

            risk_badge = f' <span class="badge-xs warn-bg">{_esc(tbo_risks)}</span>' if tbo_risks and tbo_risks != "—" else ""
            blocker_badge = f' <span class="badge-xs st-block">{_esc(tbo_blockers)}</span>' if tbo_blockers and tbo_blockers != "—" else ""

            rows += f"""<tr>
                <td><span class="badge-xs {s_class}">{_esc(tbo_status)}</span></td>
                <td class="mono">{_esc(tbo_id)}</td>
                <td>
                    <div class="tbo-name">{_esc(tbo_name)}</div>
                    <div class="tbo-meta">
                        <span class="muted">{_esc(tbo_priority)}</span>
                        <span class="muted">{_esc(tbo_owner)}</span>
                        <span class="muted">Due: {_esc(tbo_due)}</span>
                        {risk_badge}{blocker_badge}
                    </div>
                </td>
                <td>
                    <div>{linked_done}/{linked_total} stories</div>
                    <div class="progress-bar"><div class="progress-fill" style="width: {story_pct}%; background: {_pct_color(story_pct)}"></div></div>
                </td>
            </tr>"""

        html += f"""
        <div class="section">
            <h2>Tangible Business Outcomes</h2>
            <table class="data-table tbo-table">
                <thead><tr><th>Status</th><th>ID</th><th>Business Outcome</th><th>Story Progress</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    else:
        html += '<div class="section"><h2>Tangible Business Outcomes</h2><p class="muted">No TBOs defined yet. Populate _living_business_objectives.md with user-facing outcomes.</p></div>'

    # --- Gantt-style timeline ---
    if objectives:
        has_dates = any(obj.get("Planned", "").strip() for obj in objectives)
        if has_dates:
            from datetime import date as _date

            # Compute date range for the chart
            today_str = str(_date.today())
            all_dates = [today_str]
            for obj in objectives:
                p = obj.get("Planned", "").strip()
                a = obj.get("Actual", "").strip()
                if p and p != "\u2014":
                    all_dates.append(p)
                if a and a != "\u2014":
                    all_dates.append(a)
            all_dates.sort()
            chart_start = all_dates[0]
            chart_end = all_dates[-1]

            # Days span for percentage calculation
            try:
                d_start = _date.fromisoformat(chart_start)
                d_end = _date.fromisoformat(chart_end)
                d_today = _date.today()
                total_days = max((d_end - d_start).days, 1)
            except (ValueError, TypeError):
                d_start = d_end = d_today = _date.today()
                total_days = 1

            today_pct = min(100, max(0, int((d_today - d_start).days / total_days * 100)))

            gantt_rows = ""
            for obj in objectives:
                tbo_id = obj.get("ID", "").strip()
                tbo_name = obj.get("TBO", obj.get("Objective", "")).strip()[:35]
                planned = obj.get("Planned", "").strip()
                actual = obj.get("Actual", "").strip()
                status = obj.get("Status", "").strip()
                s_class = _status_class(status)

                # Bar position: start at 0, end at planned date
                try:
                    d_planned = _date.fromisoformat(planned) if planned and planned != "\u2014" else d_end
                    bar_end = min(100, max(5, int((d_planned - d_start).days / total_days * 100)))
                except (ValueError, TypeError):
                    bar_end = 50

                # Determine bar color based on status
                if "DONE" in status.upper():
                    bar_color = "#22c55e"
                elif "ACCEPT" in status.upper():
                    bar_color = "#eab308"
                elif "IN_PROGRESS" in status.upper():
                    bar_color = "#3b82f6"
                else:
                    bar_color = "#64748b"

                # Actual marker
                actual_marker = ""
                if actual and actual != "\u2014":
                    try:
                        d_actual = _date.fromisoformat(actual)
                        actual_pos = min(100, max(0, int((d_actual - d_start).days / total_days * 100)))
                        actual_marker = f'<div style="position:absolute;left:{actual_pos}%;top:0;bottom:0;width:3px;background:#22c55e;border-radius:2px;" title="Actual: {_esc(actual)}"></div>'
                    except (ValueError, TypeError):
                        pass

                # Date labels on the bar
                planned_label = ""
                if planned and planned != "\u2014":
                    planned_label = f'<div style="position:absolute;right:4px;top:3px;color:#fff;opacity:0.9;white-space:nowrap;">P: {_esc(planned)}</div>'
                actual_label = ""
                if actual and actual != "\u2014":
                    actual_label = f'<div style="position:absolute;left:4px;top:3px;color:#fff;opacity:0.9;white-space:nowrap;">A: {_esc(actual)}</div>'

                gantt_rows += f"""
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.6rem;">
                    <div style="width:80px;flex-shrink:0;" class="mono">{_esc(tbo_id)}</div>
                    <div style="width:200px;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{_esc(tbo_name)}</div>
                    <div style="flex:1;position:relative;height:28px;background:#1e293b;border-radius:4px;overflow:hidden;">
                        <div style="position:absolute;left:0;top:0;bottom:0;width:{bar_end}%;background:{bar_color};border-radius:4px;opacity:0.8;"></div>
                        {actual_marker}
                        {planned_label}
                        {actual_label}
                    </div>
                    <div style="width:70px;flex-shrink:0;text-align:center;"><span class="badge-xs {s_class}">{_esc(status)}</span></div>
                </div>
                """

            html += f"""
            <div class="section">
                <h2>Timeline</h2>
                <div style="display:flex;gap:1.5rem;margin-bottom:0.75rem;flex-wrap:wrap;">
                    <span style="display:flex;align-items:center;gap:0.3rem;"><span style="width:12px;height:12px;border-radius:2px;background:#22c55e;display:inline-block;"></span> Done</span>
                    <span style="display:flex;align-items:center;gap:0.3rem;"><span style="width:12px;height:12px;border-radius:2px;background:#eab308;display:inline-block;"></span> Ready for Acceptance</span>
                    <span style="display:flex;align-items:center;gap:0.3rem;"><span style="width:12px;height:12px;border-radius:2px;background:#3b82f6;display:inline-block;"></span> In Progress</span>
                    <span style="display:flex;align-items:center;gap:0.3rem;"><span style="width:12px;height:12px;border-radius:2px;background:#64748b;display:inline-block;"></span> Not Started</span>
                    <span style="display:flex;align-items:center;gap:0.3rem;"><span style="width:3px;height:12px;background:#eab308;display:inline-block;"></span> Today</span>
                    <span style="display:flex;align-items:center;gap:0.3rem;"><span style="width:3px;height:12px;background:#22c55e;display:inline-block;"></span> Actual Completion</span>
                </div>
                <div style="position:relative;padding:0.5rem 0;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;margin-left:336px;">
                        <span class="muted">{chart_start}</span>
                        <span style="color:#eab308;font-weight:bold;">Today ({today_str})</span>
                        <span class="muted">{chart_end}</span>
                    </div>
                    <div style="position:relative;">
                        <div style="position:absolute;left:calc(336px + {today_pct}% * (100% - 336px) / 100);top:0;bottom:0;width:2px;background:#eab308;opacity:0.5;z-index:1;"></div>
                        {gantt_rows}
                    </div>
                </div>
            </div>
            """

    return f'<div class="section">{html}</div>'


# --- Tab: Roadmap ---


def _tab_roadmap(docs_dir: Path) -> str:
    """Roadmap tab — TBO→Story→Task workbook view with PM attributes.

    Uses the shared workbook model. Shows full lineage, planned/actual dates,
    DoD, task type (F/NF/SHADOW). This is the single place to see the full picture.
    """
    from devlead.workbook import load_workbook

    wb = load_workbook(docs_dir)

    if not wb.tbos:
        return '<div class="section"><p class="muted">No TBOs defined. Populate _living_business_objectives.md.</p></div>'

    html = ""

    for tbo in wb.tbos:
        s_class = _status_class(tbo.status)
        s_done = tbo.stories_done
        s_total = tbo.stories_total
        t_done = tbo.tasks_done
        t_total = tbo.tasks_total
        s_pct = int(s_done / s_total * 100) if s_total > 0 else 0

        planned = tbo.planned if tbo.planned and tbo.planned.strip() != "\u2014" else ""
        actual = tbo.actual if tbo.actual and tbo.actual.strip() != "\u2014" else ""
        dates_html = ""
        if planned:
            dates_html += f'<span class="muted">Planned: {_esc(planned)}</span> '
        if actual:
            dates_html += f'<span class="muted">Actual: {_esc(actual)}</span>'

        html += f"""
        <div class="roadmap-epic">
            <div style="color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Tangible Business Outcome</div>
            <div class="epic-header">
                <span style="font-weight: 700; color: var(--accent);">{_esc(tbo.id)}</span>
                <span class="epic-name">{_esc(tbo.objective)}</span>
                <span class="badge {s_class}">{_esc(tbo.status)}</span>
            </div>
            <div style="padding: 0 1rem; display: flex; gap: 1.5rem; align-items: center;">
                <span class="muted">{s_done}/{s_total} stories</span>
                <span class="muted">{t_done}/{t_total} tasks</span>
                {dates_html}
                <div class="progress-bar" style="flex: 1; max-width: 200px;">
                    <div class="progress-fill" style="width: {s_pct}%; background: {_pct_color(s_pct)}"></div>
                </div>
            </div>
        """

        if tbo.stories:
            html += '<div style="margin: 0.5rem 1rem 1rem;">'
            for story in tbo.stories:
                st_class = _status_class(story.status)
                s_tokens = f"{story.total_tokens:,}" if story.total_tokens else "&mdash;"
                s_sessions = str(story.session_count) if story.session_count else "&mdash;"
                task_done = sum(1 for t in story.tasks if "DONE" in t.status.upper())
                task_total = len(story.tasks)

                html += f"""
                <details style="margin-bottom: 4px; border-left: 2px solid var(--blue); padding-left: 12px;">
                    <summary style="cursor: pointer; padding: 6px 0; display: flex; align-items: center; gap: 8px;">
                        <span class="badge-xs {st_class}">{_esc(story.status)}</span>
                        <span class="mono" style="color: var(--blue);">{_esc(story.id)}</span>
                        <span>{_esc(story.description[:60])}</span>
                        <span class="muted">{task_done}/{task_total} tasks</span>
                        <span class="muted">Tokens: {s_tokens}</span>
                        <span class="muted">{f'{story.duration_min} min' if story.duration_min else ''}</span>
                    </summary>
                """
                if story.tasks:
                    html += """<table class="data-table" style="margin: 4px 0 8px 0;">
                        <thead><tr><th>Task</th><th>Description</th><th>Status</th><th>Req Type</th><th>Tokens</th><th>Sessions</th><th>Duration</th></tr></thead><tbody>"""
                    for task in story.tasks:
                        tt_class = _status_class(task.status)
                        type_class = "st-done" if task.task_type == "F" else "st-progress" if task.task_type == "NF" else "st-block"
                        t_tokens = f"{task.total_tokens:,}" if task.total_tokens else "&mdash;"
                        t_sessions = str(task.session_count) if task.session_count else "&mdash;"
                        html += f"""<tr>
                            <td class="mono">{_esc(task.id)}</td>
                            <td>{_esc(task.description[:50])}</td>
                            <td><span class="badge-xs {tt_class}">{_esc(task.status)}</span></td>
                            <td><span class="badge-xs {type_class}">{_esc(task.task_type)}</span></td>
                            <td class="mono">{t_tokens}</td>
                            <td class="mono">{t_sessions}</td>
                            <td class="mono">{f'{task.duration_min} min' if task.duration_min else '&mdash;'}</td>
                        </tr>"""
                    html += "</tbody></table>"
                html += "</details>"
            html += "</div>"

        html += "</div>"

    # Shadow work
    if wb.shadow_tasks:
        html += f"""
        <div class="section orphan-section">
            <h3>Shadow Work <span class="muted">({len(wb.shadow_tasks)} items — no TBO linkage)</span></h3>
            <table class="data-table"><thead><tr>
                <th>Task</th><th>Description</th><th>Status</th><th>Req Type</th><th>Linked To</th>
            </tr></thead><tbody>
        """
        for t in wb.shadow_tasks:
            tt_class = _status_class(t.status)
            type_class = "st-progress" if t.task_type == "NF" else "st-block"
            html += f"""<tr>
                <td class="mono">{_esc(t.id)}</td>
                <td>{_esc(t.description[:50])}</td>
                <td><span class="badge-xs {tt_class}">{_esc(t.status)}</span></td>
                <td><span class="badge-xs {type_class}">{_esc(t.task_type)}</span></td>
                <td class="muted">{_esc(t.story_id)}</td>
            </tr>"""
        html += "</tbody></table></div>"

    return f'<div class="section">{html}</div>'


# --- Tab: KPIs ---


def _tab_kpis(kpis: list[KpiResult]) -> str:
    categories = [
        ("A", "LLM Effectiveness", "Is the AI getting better?"),
        ("B", "Delivery & Project Management", "Is business value being produced?"),
        ("C", "Project Health", "Is the system of record healthy?"),
    ]

    sections = ""
    for cat_key, cat_name, cat_desc in categories:
        cat_kpis = [k for k in kpis if k.category == cat_key]
        if not cat_kpis:
            continue

        rows = ""
        for k in cat_kpis:
            val = _format_kpi_value(k)
            warn_class = ' class="warn"' if k.warning else ""
            rows += f'<tr{warn_class}><td class="kpi-name">{_esc(k.name)}</td><td class="kpi-value">{val}</td><td class="kpi-detail">{_esc(k.detail)}</td></tr>'

        sections += f"""
        <div class="kpi-cat">
            <h3>{_esc(cat_name)}</h3>
            <p class="cat-desc">{_esc(cat_desc)}</p>
            <table class="data-table"><thead><tr><th>KPI</th><th>Value</th><th>Detail</th></tr></thead><tbody>{rows}</tbody></table>
        </div>
        """

    return f'<div class="section">{sections}</div>'


# --- Tab: Intake ---


def _tab_backlog(docs_dir: Path) -> str:
    """Backlog tab — scratchpad + all open FEAT/BUG/GAP items grouped by priority.

    This is the pipeline BEFORE work becomes stories/tasks.
    Scratchpad → Intake (FEAT/BUG/GAP) → Story → Task
    """
    html = ""

    # --- Scratchpad (untriaged ideas) ---
    scratchpad = _load_table(docs_dir / "_scratchpad.md")
    pending = [s for s in scratchpad if s.get("Status", "").upper() == "PENDING"]
    if pending:
        rows = ""
        for item in pending:
            rows += f"""<tr>
                <td class="mono">{_esc(item.get("Key", ""))}</td>
                <td>{_esc(item.get("Item", ""))}</td>
                <td class="muted">{_esc(item.get("Source", ""))}</td>
                <td class="muted">{_esc(item.get("Added", ""))}</td>
            </tr>"""
        html += f"""
        <div class="kpi-cat">
            <h3>Scratchpad <span class="count">({len(pending)} pending triage)</span></h3>
            <table class="data-table"><thead><tr><th>Key</th><th>Item</th><th>Source</th><th>Added</th></tr></thead><tbody>{rows}</tbody></table>
        </div>
        """

    # --- Collect all open intake items ---
    all_items: list[dict] = []
    for fname, label in [
        ("_intake_features.md", "FEAT"),
        ("_intake_bugs.md", "BUG"),
        ("_intake_gaps.md", "GAP"),
    ]:
        items = _load_table(docs_dir / fname)
        for item in items:
            if item.get("Status", "").upper() == "OPEN":
                item["_type"] = label
                all_items.append(item)

    if all_items:
        # Group by priority
        by_priority: dict[str, list[dict]] = {}
        for item in all_items:
            p = item.get("Priority", "P3").strip()
            by_priority.setdefault(p, []).append(item)

        for priority in ["P1", "P2", "P3"]:
            items = by_priority.get(priority, [])
            if not items:
                continue
            rows = ""
            for item in items:
                type_label = item.get("_type", "?")
                type_color = {"FEAT": "st-progress", "BUG": "st-block", "GAP": "warn-bg"}.get(type_label, "")
                rows += f"""<tr>
                    <td><span class="badge-xs {type_color}">{_esc(type_label)}</span></td>
                    <td class="mono">{_esc(item.get("Key", ""))}</td>
                    <td>{_esc(item.get("Item", "")[:80])}</td>
                    <td class="muted">{_esc(item.get("Added", ""))}</td>
                </tr>"""
            html += f"""
            <div class="kpi-cat">
                <h3>{priority} <span class="count">({len(items)} items)</span></h3>
                <table class="data-table"><thead><tr><th>Type</th><th>Key</th><th>Item</th><th>Added</th></tr></thead><tbody>{rows}</tbody></table>
            </div>
            """

    # --- Summary ---
    total_open = len(all_items)
    total_scratch = len(pending)
    html += f"""
    <div class="section" style="margin-top:1rem;">
        <div class="muted">{total_scratch} scratchpad items pending triage | {total_open} open backlog items</div>
    </div>
    """

    if not all_items and not pending:
        html = '<p class="muted">Backlog is empty. All items have been promoted to stories or archived.</p>'

    return f'<div class="section">{html}</div>'


# --- Tab: Session ---


def _tab_session(state: dict, project_dir: Path | None = None) -> str:
    timeline = _timeline_section(state)
    checklist = _checklist_section(state)
    scope = _scope_section(state)
    memory = _memory_section(project_dir) if project_dir else ""
    return timeline + checklist + scope + memory


def _memory_section(project_dir: Path | None) -> str:
    """Show Claude memory entries and their source files."""
    if not project_dir:
        return ""

    # Find memory directory — Claude stores per-project memory here
    # Path pattern: ~/.claude/projects/<encoded-project-path>/memory/
    home = Path.home()
    claude_projects = home / ".claude" / "projects"
    if not claude_projects.exists():
        return ""

    # Find matching project memory dir
    memory_dir = None
    project_str = str(project_dir.resolve()).replace("\\", "-").replace("/", "-").replace(":", "-")
    for d in claude_projects.iterdir():
        if d.is_dir() and "memory" in [c.name for c in d.iterdir() if c.is_dir()]:
            # Check if this dir name matches our project
            if project_str.lower() in d.name.lower() or d.name.lower() in project_str.lower():
                memory_dir = d / "memory"
                break

    if not memory_dir or not memory_dir.exists():
        return '<div class="section"><h2>Claude Memory</h2><p class="muted">No memory entries found for this project.</p></div>'

    # Read MEMORY.md index
    memory_index = memory_dir / "MEMORY.md"
    if not memory_index.exists():
        return '<div class="section"><h2>Claude Memory</h2><p class="muted">No MEMORY.md index found.</p></div>'

    index_text = memory_index.read_text()

    # Read individual memory files for detail
    memory_files = []
    for f in sorted(memory_dir.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        try:
            content = f.read_text()
            # Parse frontmatter
            meta = {"name": f.stem, "description": "", "type": "", "file": f.name}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            meta[k.strip()] = v.strip()
                    meta["body"] = parts[2].strip()[:200]  # first 200 chars
            else:
                meta["body"] = content.strip()[:200]
            memory_files.append(meta)
        except Exception:
            continue

    if not memory_files:
        # Just show the index
        return f'<div class="section"><h2>Claude Memory</h2><div class="status-prose">{_render_prose(index_text)}</div></div>'

    rows = ""
    type_colors = {"user": "st-prog", "feedback": "st-open", "project": "st-done", "reference": "st-default"}
    for m in memory_files:
        t_class = type_colors.get(m.get("type", ""), "st-default")
        body_preview = _esc(m.get("body", ""))[:150]
        rows += f"""<tr>
            <td><span class="badge-xs {t_class}">{_esc(m.get("type", "?"))}</span></td>
            <td class="mono">{_esc(m.get("file", ""))}</td>
            <td>{_esc(m.get("name", ""))}</td>
            <td class="muted">{_esc(m.get("description", ""))}</td>
        </tr>"""

    return f"""
    <div class="section">
        <h2>Claude Memory <span class="count">({len(memory_files)} entries)</span></h2>
        <p class="muted" style="margin-bottom: 12px;">What Claude remembered from this project. Better signals in your docs = better memory.</p>
        <table class="data-table">
            <thead><tr><th>Type</th><th>File</th><th>Name</th><th>Description</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """


# --- Tab: Audit ---


def _tab_audit(entries: list[dict]) -> str:
    """Audit tab — governance actions, not raw file edits.

    Filters out .py source file edits. Shows: claude_docs changes,
    memory writes, cross-project detections, scope violations.
    """
    if not entries:
        return '<div class="section"><p class="muted">No governance actions recorded this session.</p></div>'

    # Filter: only show governance-relevant entries
    governance_entries = []
    source_edits = 0
    for e in entries:
        fp = e.get("file_path", "")
        cross = e.get("cross_project", False)
        norm = fp.replace("\\", "/")

        # Always show: cross-project, memory writes, claude_docs edits, config edits
        if cross or "/claude_docs/" in norm or "/.claude/" in norm or "/memory/" in norm or "devlead.toml" in norm:
            governance_entries.append(e)
        elif norm.endswith(".py") or norm.endswith(".js") or norm.endswith(".ts"):
            source_edits += 1  # count but don't show
        else:
            governance_entries.append(e)

    rows = ""
    for e in governance_entries:
        ts = e.get("timestamp", "?")[:19]
        tool = e.get("tool_name", "?")
        fp = e.get("file_path", "?")
        st = e.get("state", "?")
        cross = e.get("cross_project", False)
        agent = e.get("agent_type", "")

        cross_badge = ' <span class="badge-xs warn-bg">CROSS</span>' if cross else ""
        agent_badge = f' <span class="badge-xs blue-bg">{_esc(agent)}</span>' if agent else ""
        warn = ' class="warn"' if cross else ""

        rows += f'<tr{warn}><td class="mono">{_esc(ts)}</td><td><span class="badge-xs {_status_class(st)}">{_esc(st)}</span></td><td>{_esc(tool)}</td><td class="fp">{_esc(fp)}{cross_badge}{agent_badge}</td></tr>'

    summary = f"{len(governance_entries)} governance actions"
    if source_edits:
        summary += f" | {source_edits} source edits filtered"

    return f"""
    <div class="section">
        <h2>Governance Audit <span class="count">({summary})</span></h2>
        <p class="muted">Shows: doc updates, memory writes, config changes, cross-project detections. Source code edits (.py) filtered out.</p>
        <table class="data-table"><thead><tr><th>Time</th><th>State</th><th>Tool</th><th>File</th></tr></thead><tbody>{rows}</tbody></table>
    </div>
    """


# --- Tab: Trends ---


def _tab_trends(history: list[dict], deltas: dict) -> str:
    """Session-over-session trends and deltas."""
    if not history:
        return '<div class="section"><p class="muted">No session history yet. Complete a session to start tracking trends.</p></div>'

    html = ""

    # Delta cards — what changed since last session
    if deltas:
        key_metrics = [
            ("convergence", "Convergence", "%", True),   # higher is better
            ("tasks_done", "Tasks Done", "", True),
            ("tasks_total", "Total Tasks", "", None),     # neutral
            ("intake_open", "Open Intake", "", False),    # lower is better
            ("stories_done", "Stories Done", "", True),
            ("tasks_blocked", "Blocked", "", False),
            ("tasks_overdue", "Overdue", "", False),
        ]

        cards = ""
        for key, label, suffix, higher_is_better in key_metrics:
            if key not in deltas:
                continue
            val = deltas[key]
            if val == 0:
                arrow = "―"
                color = "var(--muted)"
            elif val > 0:
                arrow = f"+{val:.0f}{suffix}"
                if higher_is_better is True:
                    color = "var(--green)"
                elif higher_is_better is False:
                    color = "var(--red)"
                else:
                    color = "var(--muted)"
            else:
                arrow = f"{val:.0f}{suffix}"
                if higher_is_better is True:
                    color = "var(--red)"
                elif higher_is_better is False:
                    color = "var(--green)"
                else:
                    color = "var(--muted)"

            cards += f"""
            <div class="stat-card">
                <div class="stat-value" style="color: {color}">{arrow}</div>
                <div class="stat-label">{label}</div>
            </div>
            """

        html += f'<div class="section"><h2>Changes Since Last Session</h2><div class="stat-grid">{cards}</div></div>'

    # History table — all sessions
    if len(history) >= 1:
        rows = ""
        for h in reversed(history[-10:]):  # Last 10 sessions
            d = h.get("date", "?")
            conv = h.get("convergence", 0)
            tasks_d = h.get("tasks_done", 0)
            tasks_t = h.get("tasks_total", 0)
            intake_o = h.get("intake_open", 0)
            stories_d = h.get("stories_done", 0)
            transitions = h.get("transitions", 0)

            rows += f"""<tr>
                <td class="mono">{_esc(str(d))}</td>
                <td style="color: {_pct_color(conv)}">{conv:.0f}%</td>
                <td>{tasks_d}/{tasks_t}</td>
                <td>{stories_d}</td>
                <td style="color: {'var(--red)' if intake_o > 5 else 'var(--text)'}">{intake_o}</td>
                <td>{transitions}</td>
            </tr>"""

        html += f"""
        <div class="section">
            <h2>Session History <span class="count">(last {min(len(history), 10)})</span></h2>
            <table class="data-table">
                <thead><tr><th>Date</th><th>Convergence</th><th>Tasks</th><th>Stories Done</th><th>Open Intake</th><th>Transitions</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """

    # Drift detection
    if len(history) >= 3:
        recent = history[-3:]
        conv_values = [h.get("convergence", 0) for h in recent]
        if conv_values[-1] < conv_values[0]:
            drift = conv_values[0] - conv_values[-1]
            html += f"""
            <div class="section">
                <div class="nba-box" style="border-color: var(--red);">
                    DRIFT DETECTED: Convergence dropped {drift:.0f}% over last 3 sessions
                    ({conv_values[0]:.0f}% &rarr; {conv_values[-1]:.0f}%).
                    Business objectives are moving backward.
                </div>
            </div>
            """
        elif conv_values[-1] > conv_values[0]:
            gain = conv_values[-1] - conv_values[0]
            html += f"""
            <div class="section">
                <div class="nba-box">
                    ON TRACK: Convergence gained {gain:.0f}% over last 3 sessions
                    ({conv_values[0]:.0f}% &rarr; {conv_values[-1]:.0f}%).
                </div>
            </div>
            """

    return f'<div class="section">{html}</div>'


# --- Tab: Distribution ---


def _tab_distribution(docs_dir: Path) -> str:
    """Distribution / productionization tab."""
    dist_text = _read_safe(docs_dir / "_living_distribution.md")
    dist_table = _load_table(docs_dir / "_living_distribution.md")

    if not dist_text:
        return '<div class="section"><p class="muted">No distribution data. Create _living_distribution.md to track your go-to-market plan.</p></div>'

    html = ""

    # Distribution channels table
    if dist_table:
        rows = ""
        for item in dist_table:
            s_class = _status_class(item.get("Status", ""))
            # Flexible — works with any columns
            cols = list(item.values())
            cells = "".join(f"<td>{_esc(c)}</td>" for c in cols)
            rows += f"<tr>{cells}</tr>"
        headers = list(dist_table[0].keys())
        header_cells = "".join(f"<th>{_esc(h)}</th>" for h in headers)
        html += f"""
        <div class="section">
            <h2>Distribution Channels</h2>
            <table class="data-table"><thead><tr>{header_cells}</tr></thead><tbody>{rows}</tbody></table>
        </div>
        """

    # Render prose sections
    for section_name in ["Funnel", "Launch Checklist", "Pricing", "Go-to-Market"]:
        section = _extract_section(dist_text, section_name)
        if section and section.strip() and not section.strip().startswith("_"):
            # Check if section has a table
            section_table = parse_table(section)
            if section_table:
                headers = list(section_table[0].keys())
                header_cells = "".join(f"<th>{_esc(h)}</th>" for h in headers)
                rows = ""
                for item in section_table:
                    cells = "".join(f"<td>{_esc(v)}</td>" for v in item.values())
                    rows += f"<tr>{cells}</tr>"
                html += f'<div class="section"><h2>{_esc(section_name)}</h2><table class="data-table"><thead><tr>{header_cells}</tr></thead><tbody>{rows}</tbody></table></div>'
            else:
                html += f'<div class="section"><h2>{_esc(section_name)}</h2><div class="status-prose">{_render_prose(section)}</div></div>'

    if not html:
        html = '<div class="section"><p class="muted">Populate _living_distribution.md with your go-to-market plan.</p></div>'

    return f'<div class="section">{html}</div>'


# --- Helpers ---


def _extract_section(text: str, heading: str) -> str:
    """Extract content under a ## heading until the next ## or end."""
    lines = text.splitlines()
    capture = False
    result = []
    for line in lines:
        if line.strip().startswith("## ") and heading.lower() in line.lower():
            capture = True
            continue
        elif line.strip().startswith("## ") and capture:
            break
        elif capture:
            result.append(line)
    return "\n".join(result).strip()


def _render_prose(text: str) -> str:
    """Render markdown-ish text to simple HTML."""
    html = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            html += f"<li>{_esc(stripped[2:])}</li>"
        elif stripped:
            html += f"<p>{_esc(stripped)}</p>"
    return html


def _prose_section(title: str, text: str) -> str:
    """Render a full text section with heading and prose."""
    rendered = _render_prose(text)
    if not rendered:
        return ""
    return f'<div class="section"><h2>{_esc(title)}</h2><div class="status-prose">{rendered}</div></div>'


def _esc(s: str) -> str:
    s = str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    s = s.replace("\u2014", "&mdash;").replace("\u2013", "&ndash;").replace("\u2192", "&rarr;")
    return s


def _pct_color(pct: float) -> str:
    if pct >= 80:
        return "#27ae60"
    if pct >= 50:
        return "#f39c12"
    return "#e74c3c"


def _status_class(status: str) -> str:
    s = status.upper()
    if "DONE" in s or "COMPLETE" in s or "CLOSED" in s:
        return "st-done"
    if "PROGRESS" in s:
        return "st-prog"
    if "BLOCK" in s:
        return "st-block"
    if "REOPEN" in s:
        return "st-reopen"
    if "OPEN" in s:
        return "st-open"
    return "st-default"


def _format_kpi_value(k: KpiResult) -> str:
    if k.format == "text":
        return "—"
    if k.format == "percent":
        return f"{k.value:.0f}%"
    if k.format == "count":
        return f"{k.value:.0f}"
    if k.format == "ratio":
        return f"{k.value:.2f}"
    if k.format == "days":
        return f"{k.value:.1f}d"
    return f"{k.value:.0f}/100"


def _wrap_html(project_name: str, today: date, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<!-- auto-refresh disabled until devlead serve preserves tab state -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DevLead — {_esc(project_name)} — {today.isoformat()}</title>
<style>
:root {{
    --bg: #0f1117; --card: #1a1d27; --border: #2a2d3a; --text: #e0e0e0;
    --muted: #888; --accent: #6c5ce7; --green: #27ae60; --yellow: #f39c12;
    --red: #e74c3c; --blue: #3498db;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg); color: var(--text);
    padding: 24px; max-width: 1280px; margin: 0 auto; line-height: 1.6;
}}
h1 {{ font-size: 1.8em; font-weight: 700; }}
h2 {{ font-size: 1.2em; font-weight: 600; margin-bottom: 16px; color: var(--accent); }}
h3 {{ font-size: 1em; font-weight: 600; margin-bottom: 8px; color: var(--blue); }}
.card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 20px;
}}
.header-card {{
    background: linear-gradient(135deg, #1a1d27 0%, #2a1d3a 100%);
    border-color: var(--accent);
}}
.header-top {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px; }}
.project-name {{ color: var(--muted); font-size: 1.2em; }}
.header-meta {{
    display: flex; gap: 16px; flex-wrap: wrap; align-items: center;
    color: var(--muted); font-size: 0.9em;
}}
.section {{ margin-bottom: 28px; }}

/* --- Tabs --- */
.tab-input {{ display: none; }}
.tab-bar {{
    display: flex; gap: 4px; border-bottom: 2px solid var(--border);
    margin-bottom: 24px; padding: 0 4px;
}}
.tab-label {{
    padding: 10px 20px; cursor: pointer; color: var(--muted);
    font-weight: 500; font-size: 0.95em; border-bottom: 2px solid transparent;
    margin-bottom: -2px; transition: all 0.2s;
}}
.tab-label:hover {{ color: var(--text); }}
.tab-panel {{ display: none; }}

/* Radio button tab switching — one rule per tab */
#tab-overview:checked ~ .tab-bar label[for="tab-overview"],
#tab-business:checked ~ .tab-bar label[for="tab-business"],
#tab-roadmap:checked ~ .tab-bar label[for="tab-roadmap"],
#tab-kpis:checked ~ .tab-bar label[for="tab-kpis"],
#tab-backlog:checked ~ .tab-bar label[for="tab-backlog"],
#tab-session:checked ~ .tab-bar label[for="tab-session"],
#tab-audit:checked ~ .tab-bar label[for="tab-audit"],
#tab-trends:checked ~ .tab-bar label[for="tab-trends"],
#tab-distribution:checked ~ .tab-bar label[for="tab-distribution"] {{
    color: var(--accent); border-bottom-color: var(--accent);
}}
#tab-overview:checked ~ .tab-panels #panel-overview,
#tab-business:checked ~ .tab-panels #panel-business,
#tab-roadmap:checked ~ .tab-panels #panel-roadmap,
#tab-kpis:checked ~ .tab-panels #panel-kpis,
#tab-backlog:checked ~ .tab-panels #panel-backlog,
#tab-session:checked ~ .tab-panels #panel-session,
#tab-audit:checked ~ .tab-panels #panel-audit,
#tab-trends:checked ~ .tab-panels #panel-trends,
#tab-distribution:checked ~ .tab-panels #panel-distribution {{ display: block; }}

/* --- Badges --- */
.badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 600; }}
.badge-sm {{ display: inline-block; padding: 3px 10px; border-radius: 16px; font-size: 0.9em; font-weight: 600; }}
.badge-xs {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; font-weight: 600; }}
.state-badge {{ background: var(--accent); color: white; }}
.st-done {{ background: var(--green); color: white; }}
.st-prog {{ background: var(--blue); color: white; }}
.st-open {{ background: #3a3d4a; color: var(--text); }}
.st-block {{ background: var(--red); color: white; }}
.st-reopen {{ background: var(--yellow); color: #222; }}
.st-default {{ background: var(--border); color: var(--text); }}
.warn-bg {{ background: var(--red); color: white; }}
.blue-bg {{ background: var(--blue); color: white; }}

/* --- Stats --- */
.stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }}
.stat-card {{
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px; text-align: center;
}}
.stat-value {{ font-size: 1.4em; font-weight: 700; }}
.stat-of {{ font-size: 0.9em; color: var(--muted); }}
.stat-label {{ color: var(--muted); font-size: 0.9em; margin-top: 4px; }}
.stat-sub {{ color: var(--muted); font-size: 0.9em; margin-top: 4px; }}
.progress-bar {{ height: 4px; background: var(--border); border-radius: 2px; margin-top: 6px; overflow: hidden; }}
.progress-fill {{ height: 100%; border-radius: 2px; }}

/* --- Tables --- */
.data-table {{ width: 100%; border-collapse: collapse; }}
.data-table th {{
    text-align: left; padding: 8px 12px; color: var(--muted); font-weight: 500;
    font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border);
}}
.data-table td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); }}
tr.warn {{ background: rgba(231, 76, 60, 0.08); }}
.kpi-name {{ font-weight: 500; }}
.kpi-value {{ font-weight: 700; font-variant-numeric: tabular-nums; }}
.kpi-detail {{ color: var(--muted); }}
.kpi-cat {{ margin-bottom: 24px; }}
.cat-desc {{ color: var(--muted); margin-bottom: 12px; }}
.fp {{ word-break: break-all; font-family: monospace; }}
.mono {{ font-family: monospace; }}
.count {{ color: var(--muted); font-weight: 400; }}
.muted {{ color: var(--muted); }}

/* --- Roadmap --- */
.roadmap-epic {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; margin-bottom: 16px;
    border-left: 3px solid var(--accent);
}}
.epic-header {{
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 8px;
}}
.epic-id {{ font-family: monospace; color: var(--accent); font-weight: 600; }}
.epic-name {{ font-weight: 600; }}
.roadmap-story {{
    margin-left: 20px; padding: 10px 16px;
    border-left: 2px solid var(--blue); margin-bottom: 8px;
}}
.story-header {{
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}}
.story-id {{ font-family: monospace; color: var(--blue); }}
.story-name {{ font-weight: 500; }}
.task-list {{ margin-left: 20px; margin-top: 6px; }}
.task-row {{
    display: flex; align-items: center; gap: 8px; padding: 4px 0;
    flex-wrap: wrap;
}}
.task-id {{ font-family: monospace; color: var(--muted); }}
.task-name {{ }}
.orphan-section {{ background: rgba(231, 76, 60, 0.05); border-radius: 8px; padding: 16px; }}

/* --- Timeline (horizontal) --- */
.timeline-h {{ display: flex; gap: 0; overflow-x: auto; padding: 16px 0; }}
.tl-step {{
    display: flex; flex-direction: column; align-items: center; min-width: 100px;
    position: relative; flex: 1;
}}
.tl-step:not(:last-child)::after {{
    content: ''; position: absolute; top: 10px; left: 50%; right: -50%;
    height: 2px; background: var(--border);
}}
.tl-dot {{
    width: 14px; height: 14px; border-radius: 50%;
    background: var(--border); border: 2px solid var(--card);
    position: relative; z-index: 1;
}}
.tl-step.active .tl-dot {{ background: var(--accent); box-shadow: 0 0 10px var(--accent); }}
.tl-label {{ font-weight: 600; margin-top: 8px; }}
.tl-time {{ color: var(--muted); font-family: monospace; }}

/* --- Checklists --- */
.ck-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.ck-group {{
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px;
}}
.ck-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
.ck-count {{ color: var(--muted); }}
.ck-item {{ padding: 3px 0; }}

/* --- Scope --- */
.scope-list {{ list-style: none; }}
.scope-list li {{
    font-family: monospace; padding: 6px 12px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 6px; margin-bottom: 4px; font-size: 0.85em;
}}

/* --- Business --- */
.convergence-hero {{ text-align: center; padding: 20px; }}
.conv-number {{ font-size: 3em; font-weight: 800; }}
.conv-label {{ color: var(--muted); margin-top: 4px; }}
.biz-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }}
.biz-epic-card {{
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px; border-left: 3px solid var(--accent);
}}
.biz-epic-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }}
.biz-epic-stats {{ display: flex; gap: 16px; color: var(--muted); margin-bottom: 6px; }}
.epic-risk {{ color: var(--yellow); margin-top: 6px; }}
.epic-block {{ color: var(--red); margin-top: 4px; }}
.vision-box {{
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.08), rgba(52, 152, 219, 0.08));
    border: 1px solid var(--border); border-radius: 8px;
    padding: 20px; font-size: 1.05em; line-height: 1.8;
}}
.tbo-table td {{ vertical-align: top; }}
.tbo-name {{ font-weight: 600; margin-bottom: 4px; }}
.tbo-meta {{ display: flex; gap: 12px; flex-wrap: wrap; }}
.nba-box {{
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.1), rgba(52, 152, 219, 0.1));
    border: 1px solid var(--accent); border-radius: 8px;
    padding: 16px; font-weight: 500; font-size: 1.05em;
}}
.status-prose {{ line-height: 1.8; }}
.status-prose h3 {{ margin-top: 12px; color: var(--blue); }}
.status-prose li {{ margin-left: 20px; list-style: disc; }}

/* --- Footer --- */
.footer {{ text-align: center; color: var(--muted); font-size: 0.8em; padding: 24px 0; }}
</style>
</head>
<body>
{body}
<div class="footer">Generated by DevLead &mdash; Lead your development. Don't let AI wander.</div>
</body>
</html>"""
