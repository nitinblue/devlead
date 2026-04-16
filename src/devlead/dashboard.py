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
                    passed, output = _run_verify(cmd, repo_root)
                    cls = "st-done" if passed else "st-block"
                    label = "PASS" if passed else "FAIL"
                    rows += f'<tr><td class="mono">{tto.id}</td><td>{_e(tto.name[:45])}</td><td><span class="badge-xs {cls}">{label}</span></td><td class="muted">{_e(output[:60])}</td></tr>'
                if rows:
                    html += f'<div class="widget"><div class="widget-head">{tbo.id}: {_e(tbo.name[:40])}</div><table class="dt"><thead><tr><th>TTO</th><th>Name</th><th>Status</th><th>Output</th></tr></thead><tbody>{rows}</tbody></table></div>'
    return html or '<p class="muted">No TTOs with verify commands.</p>'


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
