"""10-tab project management dashboard. Static HTML, CSS-only tabs, no JavaScript.

Implements TBO-003 under BO-001. Dark theme ported from v1. Widget-style
multi-column layout. Gantt bars for timelines. Runs verify: commands for DoD.
"""

from __future__ import annotations

import json
import subprocess
import re
from datetime import datetime, date, timezone
from pathlib import Path


def generate(repo_root: Path) -> str:
    repo_root = Path(repo_root).resolve()
    docs_dir = repo_root / "devlead_docs"
    today = date.today()

    from devlead import hierarchy, kpi, effort, intake, audit

    sprints = hierarchy.parse(docs_dir / "_project_hierarchy.md") if (docs_dir / "_project_hierarchy.md").exists() else []
    kpis = kpi.compute(repo_root)
    effort_data = effort.get_all_effort(docs_dir)
    sessions = kpi._read_session_history(docs_dir)

    tabs = [
        ("summary", "Summary", _tab_summary(sprints, kpis, today)),
        ("convergence", "Convergence", _tab_convergence(sprints, repo_root)),
        ("hierarchy", "Hierarchy", _tab_hierarchy(sprints)),
        ("kpis", "KPIs", _tab_kpis(kpis)),
        ("timelines", "Timelines", _tab_timelines(sprints, today)),
        ("tokens", "Tokens", _tab_tokens(sessions, effort_data, kpis)),
        ("intake", "Intake", _tab_intake(docs_dir, intake)),
        ("audit", "Audit", _tab_audit(docs_dir)),
        ("dod", "Def of Done", _tab_dod(sprints, repo_root)),
        ("sessions", "Sessions", _tab_sessions(sessions)),
        ("changes", "Changes", _tab_changes(sprints)),
    ]

    tab_ids = [t[0] for t in tabs]
    body = _build_tabs(tabs, tab_ids)
    header = _header(sprints, repo_root.name, today)
    return _wrap_html(repo_root.name, today, header + body, tab_ids)


def write_dashboard(repo_root: Path) -> Path:
    repo_root = Path(repo_root).resolve()
    html = generate(repo_root)
    out_dir = repo_root / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"dashboard-{date.today().isoformat()}.html"
    out.write_text(html, encoding="utf-8")
    return out


def _header(sprints, name, today):
    conv = f"{sprints[0].convergence:.1f}" if sprints else "0"
    sprint_name = sprints[0].name if sprints else "No sprint"
    bo_count = sum(len(s.bos) for s in sprints)
    tto_total = sum(1 for s in sprints for b in s.bos for t in b.tbos for tt in t.ttos)
    tto_done = sum(1 for s in sprints for b in s.bos for t in b.tbos for tt in t.ttos if tt.done)
    return f"""
    <div class="header">
      <div class="header-left"><h1>{_e(name)}</h1><span class="muted">{sprint_name} &middot; {today.isoformat()}</span></div>
      <div class="header-right"><div class="hero-num">{conv}%</div><div class="muted">convergence</div></div>
      <div class="header-right"><div class="hero-num">{tto_done}/{tto_total}</div><div class="muted">TTOs verified</div></div>
      <div class="header-right"><div class="hero-num">{bo_count}</div><div class="muted">BOs</div></div>
    </div>"""


def _tab_summary(sprints, kpis, today):
    if not sprints:
        return '<p class="muted">No hierarchy data.</p>'
    cards = ""
    for bo in sprints[0].bos:
        conv = bo.convergence
        color = _pc(conv)
        overdue = ""
        if bo.end_date and bo.end_date not in ("(pending)", "(not set)"):
            try:
                if today > datetime.strptime(bo.end_date, "%Y-%m-%d").date() and conv < 100:
                    overdue = '<span class="badge-xs st-block">OVERDUE</span>'
            except ValueError:
                pass
        cards += f'<div class="widget"><div class="widget-head">{_e(bo.id)} {overdue}</div><div class="widget-title">{_e(bo.name[:50])}</div><div class="bar"><div class="bar-fill" style="width:{conv:.0f}%;background:{color}"></div></div><div class="widget-foot">{conv:.1f}% &middot; wt:{bo.weight} &middot; {_e(bo.end_date)}</div></div>'
    nba = ""
    for k in kpis:
        if k.name == "Next Best Action" and k.detail:
            nba = f'<div class="nba">{_e(k.detail)}</div>'
            break
    return f'{nba}<div class="grid-3">{cards}</div>'


def _tab_hierarchy(sprints):
    if not sprints:
        return '<p class="muted">No hierarchy.</p>'
    html = ""
    for s in sprints:
        html += f'<h3>{_e(s.name)} — {s.convergence:.1f}%</h3>'
        for bo in s.bos:
            bc = _pc(bo.convergence)
            html += f'<div class="bo-card"><div class="bo-head"><span class="mono">{bo.id}</span> {_e(bo.name[:60])} <span class="badge-sm" style="background:{bc};color:#fff">{bo.convergence:.0f}%</span> <span class="muted">wt:{bo.weight}</span></div>'
            for tbo in bo.tbos:
                tc = _pc(tbo.convergence)
                done = sum(1 for t in tbo.ttos if t.done)
                html += f'<div class="tbo-card"><div class="tbo-head"><span class="mono">{tbo.id}</span> {_e(tbo.name[:55])} <span style="color:{tc}">{tbo.convergence:.0f}%</span> <span class="muted">{done}/{len(tbo.ttos)}</span></div>'
                for tto in tbo.ttos:
                    icon = "&#x2705;" if tto.done else "&#x26AA;"
                    tp = "F" if tto.ttype == "functional" else "NF"
                    html += f'<div class="tto-row">{icon} <span class="mono">{tto.id}</span> {_e(tto.name[:50])} <span class="muted">wt:{tto.weight} [{tp}]</span></div>'
                html += "</div>"
            html += "</div>"
    return html


def _tab_kpis(kpis):
    cats = {"A": "LLM Effectiveness", "B": "Delivery", "C": "Project Health", "D": "Business Convergence"}
    html = '<div class="grid-2">'
    for ck, cn in cats.items():
        rows = ""
        for k in kpis:
            if k.category != ck:
                continue
            v = f"{k.value}%" if k.fmt == "percent" else f"{int(k.value)}" if k.fmt == "count" else f"{k.value:.2f}" if k.fmt == "ratio" else "—"
            warn = ' class="warn"' if k.warning else ""
            rows += f'<tr{warn}><td>{_e(k.name)}</td><td class="kpi-val">{v}</td><td class="muted">{_e(k.detail[:60])}</td></tr>'
        html += f'<div class="widget"><div class="widget-head">{cn}</div><table class="dt"><thead><tr><th>KPI</th><th>Value</th><th>Detail</th></tr></thead><tbody>{rows}</tbody></table></div>'
    html += "</div>"
    return html


def _tab_timelines(sprints, today):
    if not sprints:
        return '<p class="muted">No hierarchy.</p>'
    rows = ""
    for s in sprints:
        for bo in s.bos:
            bar = _gantt_bar(bo.start_date, bo.end_date, today, bo.convergence)
            overdue_cls = ""
            if bo.end_date and bo.end_date not in ("(pending)", "(not set)", "—", ""):
                try:
                    if today > datetime.strptime(bo.end_date, "%Y-%m-%d").date() and bo.convergence < 100:
                        overdue_cls = ' class="warn"'
                except ValueError:
                    pass
            revised = bo.revised_date if bo.revised_date and bo.revised_date != "(none)" else ""
            rev_html = f'<br><span class="badge-xs st-block">REVISED: {_e(revised)}</span>' if revised else ""
            just = f'<br><span class="muted">{_e(bo.revision_justification[:60])}</span>' if revised and bo.revision_justification and bo.revision_justification != "(none)" else ""
            rows += f'<tr{overdue_cls}><td class="mono">{bo.id}</td><td>{_e(bo.name[:40])}</td><td>{bo.start_date or "—"}</td><td>{bo.end_date or "—"}{rev_html}{just}</td><td>{bar}</td></tr>'
    return f'<table class="dt"><thead><tr><th>BO</th><th>Name</th><th>Start</th><th>End</th><th>Progress</th></tr></thead><tbody>{rows}</tbody></table>'


def _gantt_bar(start_str, end_str, today, convergence):
    try:
        start = datetime.strptime(start_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return '<span class="muted">no dates</span>'
    total = max((end - start).days, 1)
    elapsed = min(max((today - start).days, 0), total)
    time_pct = int(elapsed / total * 100)
    conv_pct = int(convergence)
    color = _pc(convergence)
    behind = time_pct > conv_pct + 10
    bar_bg = "var(--red)" if behind else "var(--border)"
    return f'<div class="gantt"><div class="gantt-time" style="width:{time_pct}%;background:{bar_bg}"></div><div class="gantt-conv" style="width:{conv_pct}%;background:{color}"></div></div><span class="muted" style="font-size:0.8em">{conv_pct}% done / {time_pct}% time</span>'


def _tab_tokens(sessions, effort_data, kpis):
    html = '<div class="grid-2">'
    if sessions:
        rows = "".join(f'<tr><td>{_e(s.get("ts","?")[:10])}</td><td>{s.get("tokens_used",0):,}</td><td>{s.get("convergence",0):.1f}%</td></tr>' for s in sessions[-10:])
        html += f'<div class="widget"><div class="widget-head">Tokens per Session</div><table class="dt"><thead><tr><th>Date</th><th>Tokens</th><th>Conv</th></tr></thead><tbody>{rows}</tbody></table></div>'
    else:
        html += '<div class="widget"><div class="widget-head">Tokens per Session</div><p class="muted">No session history yet.</p></div>'
    if effort_data:
        rows = "".join(f'<tr><td class="mono">{tid}</td><td>{e["total_tokens"]:,}</td><td>{e["sessions"]}</td></tr>' for tid, e in sorted(effort_data.items()))
        html += f'<div class="widget"><div class="widget-head">Tokens per TTO</div><table class="dt"><thead><tr><th>TTO</th><th>Tokens</th><th>Sessions</th></tr></thead><tbody>{rows}</tbody></table></div>'
    else:
        html += '<div class="widget"><div class="widget-head">Tokens per TTO</div><p class="muted">No effort data yet.</p></div>'
    total = sum(s.get("tokens_used", 0) for s in sessions)
    for k in kpis:
        if "okenomics" in k.name:
            html += f'<div class="widget"><div class="widget-head">Tokenomics</div><p class="kpi-val" style="font-size:1.5em">{int(k.value):,}</p><p class="muted">{_e(k.detail)}</p></div>'
            break
    html += f'<div class="widget"><div class="widget-head">Total Spend</div><p class="kpi-val" style="font-size:1.5em">{total:,}</p><p class="muted">{len(sessions)} sessions</p></div>'
    return html + "</div>"


def _tab_intake(docs_dir, intake_mod):
    rows = ""
    for f in sorted(docs_dir.glob("_intake_*.md")):
        for e in intake_mod.read(f):
            sc = "st-done" if e.status == "done" else "st-prog" if e.status == "in_progress" else "st-open"
            oc = "st-block" if e.origin == "forced" else "st-default"
            acts = len(e.actionable_items) if hasattr(e, 'actionable_items') and e.actionable_items else 0
            rows += f'<tr><td class="mono">{e.id}</td><td>{_e(e.title[:50])}</td><td><span class="badge-xs {sc}">{e.status}</span></td><td><span class="badge-xs {oc}">{e.origin}</span></td><td>{acts}</td></tr>'
    if not rows:
        return '<p class="muted">No intake entries.</p>'
    return f'<table class="dt"><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Origin</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table>'


def _tab_audit(docs_dir):
    log = docs_dir / "_audit_log.jsonl"
    if not log.exists():
        return '<p class="muted">No audit log.</p>'
    lines = log.read_text(encoding="utf-8").splitlines()[-100:]
    rows = ""
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
            warn = ' class="warn"' if ev.get("event") == "gate_warn" else ""
            rows += f'<tr{warn}><td class="muted">{_e(ev.get("ts","?")[:19])}</td><td>{_e(ev.get("event",""))}</td><td>{_e(ev.get("tool",""))}</td><td class="muted">{_e(str(ev.get("file",""))[-30:])}</td><td>{_e(ev.get("result",""))}</td></tr>'
        except json.JSONDecodeError:
            pass
    return f'<table class="dt"><thead><tr><th>Time</th><th>Event</th><th>Tool</th><th>File</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table>'


def _tab_dod(sprints, repo_root):
    """Read cached verify_tto events from the audit log instead of re-running.

    FEATURES-0019: previously this function shelled out to every TTO's verify:
    command at dashboard render time, taking ~45 minutes on a 67-TTO hierarchy.
    Now it just reads the audit log for the latest verify_tto event per TTO,
    written by `devlead verify-all`. To refresh stale results, the user runs
    `devlead verify-all` (which then writes new audit events).
    """
    cached = _verify_results_from_audit(repo_root)
    html = ""
    for s in sprints:
        for bo in s.bos:
            for tbo in bo.tbos:
                rows = ""
                for tto in tbo.ttos:
                    cmd = _extract_verify(tto, repo_root)
                    if not cmd:
                        rows += f'<tr><td class="mono">{tto.id}</td><td>{_e(tto.name[:45])}</td><td class="muted">no verify</td><td>—</td></tr>'
                        continue
                    res = cached.get(tto.id)
                    if res is None:
                        rows += f'<tr><td class="mono">{tto.id}</td><td>{_e(tto.name[:45])}</td><td class="muted">not yet run</td><td class="muted">run <code>devlead verify-all</code></td></tr>'
                        continue
                    passed = res.get("result") == "pass"
                    cls = "st-done" if passed else "st-block"
                    label = "PASS" if passed else "FAIL"
                    output = res.get("output", "") or ""
                    ts = res.get("ts", "")[:10]
                    rows += f'<tr><td class="mono">{tto.id}</td><td>{_e(tto.name[:45])}</td><td><span class="badge-xs {cls}">{label}</span></td><td class="muted">{_e(output[:60])} <em>({ts})</em></td></tr>'
                if rows:
                    html += f'<div class="widget"><div class="widget-head">{tbo.id}: {_e(tbo.name[:40])}</div><table class="dt"><thead><tr><th>TTO</th><th>Name</th><th>Status</th><th>Output</th></tr></thead><tbody>{rows}</tbody></table></div>'
    return html or '<p class="muted">No TTOs with verify commands.</p>'


def _verify_results_from_audit(repo_root):
    """Build {tto_id: latest_verify_event} dict from _audit_log.jsonl.

    Reads the audit log once, keeps only the most recent verify_tto event
    per TTO. O(n) where n = audit log lines. No subprocess calls.
    """
    import json
    log = repo_root / "devlead_docs" / "_audit_log.jsonl"
    out = {}
    if not log.exists():
        return out
    for line in log.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") != "verify_tto":
            continue
        tto_id = ev.get("tto_id")
        if not tto_id:
            continue
        ts = ev.get("ts", "")
        prior = out.get(tto_id)
        if prior is None or ts > prior.get("ts", ""):
            out[tto_id] = ev
    return out


def _extract_verify(tto, repo_root):
    h_path = repo_root / "devlead_docs" / "_project_hierarchy.md"
    if not h_path.exists():
        return None
    lines = h_path.read_text(encoding="utf-8").splitlines()
    found = False
    for line in lines:
        if tto.id in line and "TTO-" in line:
            found = True
            continue
        if found and line.strip().startswith("verify:"):
            return line.strip()[7:].strip()
        if found and (line.strip().startswith("- [") or line.strip().startswith("####") or line.strip().startswith("###")):
            found = False
    return None


def _run_verify(cmd, repo_root):
    if cmd.startswith("echo "):
        return False, cmd[5:].strip('"').strip("'")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15, cwd=str(repo_root))
        output = (r.stdout.strip() or r.stderr.strip() or "ok")[:80]
        return r.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)[:80]


def _tab_sessions(sessions):
    if not sessions:
        return '<p class="muted">No session history yet.</p>'
    rows = ""
    prev = 0
    for s in sessions:
        c = s.get("convergence", 0)
        d = c - prev
        dc = "color:var(--green)" if d > 0 else "color:var(--red)" if d < 0 else ""
        ds = f"+{d:.1f}" if d > 0 else f"{d:.1f}"
        rows += f'<tr><td>{_e(s.get("ts","?")[:10])}</td><td>{c:.1f}%</td><td style="{dc}">{ds}%</td><td>{s.get("tokens_used",0):,}</td></tr>'
        prev = c
    return f'<table class="dt"><thead><tr><th>Date</th><th>Conv</th><th>Delta</th><th>Tokens</th></tr></thead><tbody>{rows}</tbody></table>'


def _tab_changes(sprints):
    rows = ""
    for s in sprints:
        for bo in s.bos:
            if bo.revised_date and bo.revised_date != "(none)":
                rows += f'<tr><td class="mono">{bo.id}</td><td>{_e(bo.name[:40])}</td><td>{_e(bo.end_date)}</td><td class="warn">{_e(bo.revised_date)}</td><td>{_e(bo.revision_justification[:60])}</td></tr>'
    if not rows:
        return '<div class="nba">No deadline revisions — all BOs on track.</div>'
    return f'<table class="dt"><thead><tr><th>BO</th><th>Name</th><th>Original</th><th>Revised</th><th>Justification</th></tr></thead><tbody>{rows}</tbody></table>'


def _tab_convergence(sprints, repo_root):
    """Convergence panel — C(τ), G(τ), per-BO progress, promise vs realisation.

    Reads `_state_history.jsonl` for current metric values (overlays BO.current)
    and `_promise_ledger.jsonl` for realisation rows. BOs without metric_source
    are listed but excluded from C/G — keeps the math honest.
    """
    from devlead import convergence, metric_source, promise_ledger

    docs = repo_root / "devlead_docs"
    metric_source.apply_to_sprints(docs / metric_source.HISTORY_FILENAME, sprints)

    # Collect BOs that can compute (have metric_source declared).
    measurable = [bo for s in sprints for bo in s.bos if bo.has_metric_source]
    declared_only = [bo for s in sprints for bo in s.bos if not bo.has_metric_source]

    if not measurable and not sprints:
        return '<p class="muted">No hierarchy.</p>'

    if not measurable:
        return ('<p class="muted">No BOs have a <code>metric_source</code> declared yet — '
                'C(τ) cannot be computed. Declare <code>metric / baseline / target / metric_source</code> '
                'on a BO and run <code>devlead metric-update &lt;BO-ID&gt; &lt;value&gt;</code> '
                'to record a reading.</p>')

    # Compute C(τ) on the measurable subset, weighted by their declared BO weights.
    bo_order = sorted([bo.id for bo in measurable])
    bo_index = {bo.id: bo for bo in measurable}
    weights_raw = [bo_index[bid].weight for bid in bo_order]
    total_w = sum(weights_raw) or 1
    g = tuple(w / total_w for w in weights_raw)
    s_components = []
    for bid in bo_order:
        p = bo_index[bid].normalised_progress
        s_components.append(p if p is not None else 0.0)
    s = tuple(s_components)
    C = convergence.compute_C(s, g)

    # G(τ) — gravity over realised promise-ledger entries
    ledger_rows = promise_ledger.read_all(docs / promise_ledger.LEDGER_FILENAME)
    realised_rows = [r for r in ledger_rows if r.get("status") in ("realised", "partial", "vapor")]
    realised_vectors = []
    for r in realised_rows:
        rd = r.get("realised") or {}
        realised_vectors.append(tuple(float(rd.get(bid, 0.0)) for bid in bo_order))
    G = convergence.compute_gravity(realised_vectors, g) if realised_vectors else None

    # --- Render -----------------------------------------------------------
    if G is None:
        gravity_block = (
            '<div class="widget"><div class="widget-head">Gravity G(&tau;)</div>'
            '<div class="hero-num">—</div>'
            '<div class="muted">no realised TTOs yet</div></div>'
        )
    else:
        gravity_block = (
            f'<div class="widget"><div class="widget-head">Gravity G(&tau;)</div>'
            f'<div class="hero-num">{G:.2f}</div>'
            f'<div class="muted">over {len(realised_vectors)} realised TTOs</div></div>'
        )
    headline = (
        f'<div class="grid-2" style="margin-bottom:14px;">'
        f'<div class="widget"><div class="widget-head">Convergence C(&tau;)</div>'
        f'<div class="hero-num" style="color:{_pc(C * 100)}">{C * 100:.1f}%</div>'
        f'<div class="muted">computed across {len(measurable)} measurable BO(s)</div></div>'
        f'{gravity_block}</div>'
    )

    # Per-BO progress
    bo_rows = ""
    for bo in measurable:
        p = bo.normalised_progress or 0.0
        pct = max(0.0, min(p * 100, 110))  # clamp render width
        bar_color = _pc(p * 100)
        bo_rows += (
            f'<tr><td class="mono">{bo.id}</td><td>{_e(bo.name[:50])}</td>'
            f'<td>{bo.metric or "—"}</td>'
            f'<td>{bo.baseline if bo.baseline is not None else "—"}</td>'
            f'<td>{bo.current if bo.current is not None else "—"}</td>'
            f'<td>{bo.target if bo.target is not None else "—"}</td>'
            f'<td><div class="bar"><div class="bar-fill" style="width:{pct}%;background:{bar_color}"></div></div>'
            f' <span class="muted">{p * 100:.0f}%</span></td></tr>'
        )
    declared_rows = ""
    for bo in declared_only:
        declared_rows += (
            f'<tr><td class="mono">{bo.id}</td><td>{_e(bo.name[:50])}</td>'
            f'<td colspan="5" class="muted">no metric_source declared — excluded from C(&tau;)</td></tr>'
        )

    bo_table = (
        f'<div class="widget"><div class="widget-head">Per-BO progress</div>'
        f'<table class="dt"><thead><tr><th>BO</th><th>Name</th><th>Metric</th><th>Baseline</th>'
        f'<th>Current</th><th>Target</th><th>Progress</th></tr></thead>'
        f'<tbody>{bo_rows}{declared_rows}</tbody></table></div>'
    )

    # Promise vs realisation
    if not ledger_rows:
        ledger_html = '<div class="nba">No promise-ledger entries yet — verify a TTO with intent_vector to populate.</div>'
    else:
        prl_rows = ""
        for r in ledger_rows:
            status = r.get("status", "pending")
            phi = r.get("phi")
            eps = r.get("epsilon")
            phi_s = f"{phi:.2f}" if phi is not None else "—"
            eps_s = f"{eps:.2f}" if eps is not None else "—"
            promised_s = ", ".join(f"{k}: {v:.2f}" for k, v in (r.get("promised") or {}).items())
            realised_d = r.get("realised") or {}
            realised_s = ", ".join(f"{k}: {v:.2f}" for k, v in realised_d.items()) if realised_d else "—"
            status_cls = {"realised": "st-good", "partial": "st-warn", "vapor": "st-bad",
                          "pending": "muted"}.get(status, "")
            prl_rows += (
                f'<tr><td class="mono">{_e(r.get("tto_id", "?"))}</td>'
                f'<td>{_e(promised_s)}</td><td>{_e(realised_s)}</td>'
                f'<td>{phi_s}</td><td>{eps_s}</td>'
                f'<td><span class="{status_cls}">{status}</span></td></tr>'
            )
        ledger_html = (
            f'<div class="widget"><div class="widget-head">Promise &middot; Realisation</div>'
            f'<table class="dt"><thead><tr><th>TTO</th><th>Promised</th><th>Realised</th>'
            f'<th>&phi;</th><th>&epsilon;</th><th>Status</th></tr></thead>'
            f'<tbody>{prl_rows}</tbody></table></div>'
        )

    return headline + bo_table + ledger_html


def _build_tabs(tabs, tab_ids):
    inputs = labels = panels = ""
    for i, (tid, label, content) in enumerate(tabs):
        checked = " checked" if i == 0 else ""
        inputs += f'<input type="radio" name="tabs" id="tab-{tid}"{checked} class="tab-input">\n'
        labels += f'<label for="tab-{tid}" class="tab-label">{label}</label>\n'
        panels += f'<div class="tab-panel" id="panel-{tid}">{content}</div>\n'
    return f'<div class="tabs">{inputs}<div class="tab-bar">{labels}</div><div class="tab-panels">{panels}</div></div>'


def _e(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _pc(pct):
    if pct >= 80: return "var(--green)"
    if pct >= 50: return "var(--yellow)"
    return "var(--red)"


def _wrap_html(name, today, body, tab_ids):
    tab_css = "\n".join(
        f"#tab-{t}:checked ~ .tab-bar label[for='tab-{t}'] {{ color:var(--accent); border-bottom-color:var(--accent); }}\n#tab-{t}:checked ~ .tab-panels #panel-{t} {{ display:block; }}"
        for t in tab_ids
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DevLead — {_e(name)}</title>
<style>
:root {{ --bg:#0f1117; --card:#1a1d27; --border:#2a2d3a; --text:#e0e0e0; --muted:#888; --accent:#6c5ce7; --green:#27ae60; --yellow:#f39c12; --red:#e74c3c; --blue:#3498db; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:var(--bg); color:var(--text); padding:24px; max-width:1400px; margin:0 auto; line-height:1.5; font-size:14px; }}
h1 {{ font-size:1.5em; font-weight:700; }}
h3 {{ font-size:1.05em; color:var(--accent); margin:16px 0 10px; }}
.header {{ display:flex; align-items:center; gap:28px; padding:18px 22px; background:linear-gradient(135deg,#1a1d27,#2a1d3a); border:1px solid var(--accent); border-radius:12px; margin-bottom:18px; flex-wrap:wrap; }}
.header-left {{ flex:1; }} .header-right {{ text-align:center; min-width:90px; }}
.hero-num {{ font-size:1.7em; font-weight:800; color:var(--accent); }}
.tab-input {{ display:none; }}
.tab-bar {{ display:flex; gap:2px; border-bottom:2px solid var(--border); margin-bottom:18px; overflow-x:auto; }}
.tab-label {{ padding:9px 14px; cursor:pointer; color:var(--muted); font-weight:500; font-size:0.88em; border-bottom:2px solid transparent; margin-bottom:-2px; white-space:nowrap; }}
.tab-label:hover {{ color:var(--text); }}
.tab-panel {{ display:none; }}
{tab_css}
.grid-2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(380px,1fr)); gap:14px; }}
.grid-3 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; }}
.widget {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; margin-bottom:10px; }}
.widget-head {{ color:var(--accent); font-weight:600; font-size:0.9em; margin-bottom:6px; }}
.widget-title {{ font-weight:500; margin-bottom:6px; }}
.widget-foot {{ color:var(--muted); font-size:0.82em; margin-top:6px; }}
.bar {{ height:5px; background:var(--border); border-radius:3px; overflow:hidden; margin-top:5px; }}
.bar-fill {{ height:100%; border-radius:3px; }}
.gantt {{ height:10px; background:var(--border); border-radius:5px; overflow:hidden; position:relative; margin-bottom:3px; }}
.gantt-time {{ position:absolute; top:0; left:0; height:100%; opacity:0.3; }}
.gantt-conv {{ position:absolute; top:0; left:0; height:100%; border-radius:5px; }}
.bo-card {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px; margin-bottom:10px; border-left:3px solid var(--accent); }}
.bo-head {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:8px; font-weight:600; font-size:0.95em; }}
.tbo-card {{ margin-left:18px; padding:8px 12px; border-left:2px solid var(--blue); margin-bottom:6px; }}
.tbo-head {{ display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:4px; font-size:0.9em; }}
.tto-row {{ padding:2px 0 2px 14px; font-size:0.85em; }}
.nba {{ background:linear-gradient(135deg,rgba(108,92,231,0.1),rgba(52,152,219,0.1)); border:1px solid var(--accent); border-radius:8px; padding:12px; font-weight:500; margin-bottom:14px; }}
.dt {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
.dt th {{ text-align:left; padding:7px 9px; color:var(--muted); font-weight:500; font-size:0.82em; text-transform:uppercase; border-bottom:1px solid var(--border); }}
.dt td {{ padding:6px 9px; border-bottom:1px solid var(--border); }}
tr.warn {{ background:rgba(231,76,60,0.08); }}
.warn {{ color:var(--red); }}
.kpi-val {{ font-weight:700; font-variant-numeric:tabular-nums; }}
.badge-xs {{ display:inline-block; padding:2px 7px; border-radius:10px; font-size:0.78em; font-weight:600; }}
.badge-sm {{ display:inline-block; padding:3px 9px; border-radius:12px; font-size:0.82em; font-weight:600; }}
.st-done {{ background:var(--green); color:#fff; }} .st-prog {{ background:var(--blue); color:#fff; }}
.st-open {{ background:#3a3d4a; color:var(--text); }} .st-block {{ background:var(--red); color:#fff; }}
.st-default {{ background:var(--border); color:var(--text); }}
.mono {{ font-family:monospace; font-size:0.9em; }} .muted {{ color:var(--muted); }}
.footer {{ text-align:center; color:var(--muted); font-size:0.78em; padding:20px 0; }}
</style></head><body>
{body}
<div class="footer">Generated by DevLead &middot; {_e(today.isoformat())}</div>
</body></html>"""
