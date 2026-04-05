"""KPI engine for DevLead.

30 built-in KPIs across 3 categories, custom TOML KPIs, Python plugin KPIs.
Safe formula evaluator (no eval()).
"""

import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path


# --- Data types ---


@dataclass
class KpiResult:
    """Result of a single KPI computation."""

    name: str
    value: float = 0.0
    format: str = "score"  # score, percent, count, ratio, text, days
    category: str = ""  # A, B, C, CUSTOM, PLUGIN
    detail: str = ""
    warning: bool = False


# --- Safe formula evaluator (recursive descent, no eval) ---


class _Tokenizer:
    """Tokenize a formula string into numbers, variables, operators, parens."""

    def __init__(self, text: str, variables: dict[str, float]):
        self.text = text
        self.variables = variables
        self.pos = 0
        self.tokens: list[tuple[str, float | str]] = []
        self._tokenize()
        self.idx = 0

    def _tokenize(self) -> None:
        i = 0
        text = self.text
        while i < len(text):
            c = text[i]
            if c.isspace():
                i += 1
            elif c in "+-*/()":
                self.tokens.append(("OP", c))
                i += 1
            elif c.isdigit() or c == ".":
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == "."):
                    j += 1
                self.tokens.append(("NUM", float(text[i:j])))
                i = j
            elif c.isalpha() or c == "_":
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                    j += 1
                name = text[i:j]
                self.tokens.append(("NUM", self.variables.get(name, 0.0)))
                i = j
            else:
                i += 1  # skip unknown chars

    def peek(self) -> tuple[str, float | str] | None:
        if self.idx < len(self.tokens):
            return self.tokens[self.idx]
        return None

    def consume(self) -> tuple[str, float | str] | None:
        tok = self.peek()
        if tok:
            self.idx += 1
        return tok


def evaluate_formula(formula: str, variables: dict[str, float]) -> float:
    """Evaluate an arithmetic formula with variable substitution.

    Safe recursive descent parser. No eval().
    Supports: +, -, *, /, parentheses, numeric literals, variable names.
    Division by zero returns 0.
    Unknown variables default to 0.
    """
    tokenizer = _Tokenizer(formula, variables)
    result = _parse_expr(tokenizer)
    return result


def _parse_expr(tok: _Tokenizer) -> float:
    """Parse addition/subtraction."""
    left = _parse_term(tok)
    while True:
        p = tok.peek()
        if p and p[0] == "OP" and p[1] in ("+", "-"):
            tok.consume()
            right = _parse_term(tok)
            if p[1] == "+":
                left += right
            else:
                left -= right
        else:
            break
    return left


def _parse_term(tok: _Tokenizer) -> float:
    """Parse multiplication/division."""
    left = _parse_factor(tok)
    while True:
        p = tok.peek()
        if p and p[0] == "OP" and p[1] in ("*", "/"):
            tok.consume()
            right = _parse_factor(tok)
            if p[1] == "*":
                left *= right
            else:
                left = left / right if right != 0 else 0.0
        else:
            break
    return left


def _parse_factor(tok: _Tokenizer) -> float:
    """Parse number, variable, or parenthesized expression."""
    p = tok.peek()
    if p is None:
        return 0.0

    if p[0] == "NUM":
        tok.consume()
        return float(p[1])

    if p[0] == "OP" and p[1] == "(":
        tok.consume()  # consume (
        result = _parse_expr(tok)
        # consume closing paren
        cp = tok.peek()
        if cp and cp[0] == "OP" and cp[1] == ")":
            tok.consume()
        return result

    if p[0] == "OP" and p[1] == "-":
        tok.consume()
        return -_parse_factor(tok)

    # fallback
    tok.consume()
    return 0.0


# --- Built-in KPIs ---


def _safe_div(a: float, b: float) -> float:
    return a / b if b != 0 else 0.0


def compute_builtin_kpis(
    vars: dict[str, int | float],
    docs_dir: Path | None = None,
) -> list[KpiResult]:
    """Compute all 23 single-project built-in KPIs.

    Some KPIs require session_history.jsonl (KPIs 1-10). Without history,
    those return 0 or default values.
    """
    results = []

    # --- Category A: LLM Effectiveness ---
    # KPIs 1-10 require session history. Return defaults without it.
    # Session history integration happens in TASK-009.

    results.append(KpiResult(
        name="LLM Learning Curve",
        value=0.0,
        format="score",
        category="A",
        detail="Requires session history",
    ))

    # Going in Circles — based on reopens and blocked tasks
    circles = min(
        vars.get("tasks_reopened", 0) * 30 + vars.get("tasks_blocked", 0) * 15,
        100,
    )
    results.append(KpiResult(
        name="Going in Circles",
        value=circles,
        format="score",
        category="A",
        detail=f"{vars.get('tasks_reopened', 0)} reopened, {vars.get('tasks_blocked', 0)} blocked",
        warning=circles > 50,
    ))

    # Skin in the Game
    story_ratio = _safe_div(vars.get("tasks_with_story", 0), vars.get("tasks_active", 0))
    convergence_factor = _safe_div(vars.get("convergence", 0), 100)
    skin = min(story_ratio * 60 + convergence_factor * 40, 100)
    results.append(KpiResult(
        name="Skin in the Game",
        value=round(skin, 1),
        format="score",
        category="A",
        detail=f"{vars.get('tasks_with_story', 0)}/{vars.get('tasks_active', 0)} tasks have story ref",
    ))

    # Definition of Done — based on reopens
    dod = max(0, 100 - vars.get("tasks_reopened", 0) * 25)
    results.append(KpiResult(
        name="Definition of Done",
        value=dod,
        format="score",
        category="A",
        detail=f"{vars.get('tasks_reopened', 0)} reopened",
    ))

    # Plan Adherence — requires session history, default 0
    results.append(KpiResult(
        name="Plan Adherence",
        value=0.0,
        format="score",
        category="A",
        detail="Requires session history",
    ))

    # State Discipline — requires session history, default 0
    results.append(KpiResult(
        name="State Discipline",
        value=0.0,
        format="score",
        category="A",
        detail="Requires session history",
    ))

    # Session Completeness — requires session history, default 0
    results.append(KpiResult(
        name="Session Completeness",
        value=0.0,
        format="score",
        category="A",
        detail="Requires session history",
    ))

    # First-Time-Right
    ftr = _safe_div(
        vars.get("tasks_done", 0) - vars.get("tasks_reopened", 0),
        vars.get("tasks_done", 0),
    ) * 100
    results.append(KpiResult(
        name="First-Time-Right",
        value=round(max(ftr, 0), 1),
        format="percent",
        category="A",
        detail=f"{vars.get('tasks_done', 0) - vars.get('tasks_reopened', 0)}/{vars.get('tasks_done', 0)} stayed done",
    ))

    # Bug Introduction Rate — requires session tracking
    results.append(KpiResult(
        name="Bug Introduction Rate",
        value=vars.get("intake_open", 0),
        format="count",
        category="A",
        detail=f"{vars.get('intake_open', 0)} open issues",
    ))

    # Scope Creep — requires plan tracking
    results.append(KpiResult(
        name="Scope Creep",
        value=0,
        format="count",
        category="A",
        detail="Requires session tracking",
    ))

    # --- Category B: Delivery & Project Management ---

    # Code-Domain Convergence
    conv = _safe_div(vars.get("tasks_with_story", 0), vars.get("tasks_active", 0)) * 100
    results.append(KpiResult(
        name="Code-Domain Convergence",
        value=round(min(conv, 100), 1),
        format="score",
        category="B",
        detail=f"{vars.get('tasks_with_story', 0)}/{vars.get('tasks_active', 0)} tasks have story ref",
    ))

    # Roadmap Velocity — requires session history for avg
    results.append(KpiResult(
        name="Roadmap Velocity",
        value=vars.get("stories_done", 0),
        format="count",
        category="B",
        detail=f"{vars.get('stories_done', 0)} stories completed",
    ))

    # Intake Throughput
    throughput = _safe_div(vars.get("intake_closed", 0), vars.get("intake_total", 0)) * 100
    results.append(KpiResult(
        name="Intake Throughput",
        value=round(throughput, 1),
        format="percent",
        category="B",
        detail=f"{vars.get('intake_closed', 0)}/{vars.get('intake_total', 0)} closed",
    ))

    # Blocker Resolution — requires time tracking
    results.append(KpiResult(
        name="Blocker Resolution",
        value=vars.get("tasks_blocked", 0),
        format="count",
        category="B",
        detail=f"{vars.get('tasks_blocked', 0)} currently blocked",
    ))

    # Value per Session — requires session tracking
    results.append(KpiResult(
        name="Value per Session",
        value=0,
        format="count",
        category="B",
        detail="Requires session tracking",
    ))

    # Bug-to-Feature Ratio
    bug_ratio = _safe_div(vars.get("intake_open", 0), max(vars.get("tasks_done", 0), 1))
    results.append(KpiResult(
        name="Bug-to-Feature Ratio",
        value=round(bug_ratio, 2),
        format="ratio",
        category="B",
        detail=f"{vars.get('intake_open', 0)} issues / {vars.get('tasks_done', 0)} done",
    ))

    # Risk Concentration — simplified: tasks_blocked / tasks_active
    risk = _safe_div(vars.get("tasks_blocked", 0), vars.get("tasks_active", 0)) * 100
    results.append(KpiResult(
        name="Risk Concentration",
        value=round(min(risk, 100), 1),
        format="score",
        category="B",
        detail=f"{vars.get('tasks_blocked', 0)} blocked of {vars.get('tasks_active', 0)} active",
    ))

    # Next Best Action — text recommendation
    nba = _compute_next_best_action(vars)
    results.append(KpiResult(
        name="Next Best Action",
        value=0,
        format="text",
        category="B",
        detail=nba,
    ))

    # --- Category C: Project Health ---

    # Doc Freshness — requires file mtime, simplified
    results.append(KpiResult(
        name="Doc Freshness",
        value=0.0,
        format="score",
        category="C",
        detail="Requires file timestamps",
    ))

    # Traceability
    traceable = _safe_div(vars.get("tasks_with_story", 0), vars.get("tasks_total", 0)) * 100
    results.append(KpiResult(
        name="Traceability",
        value=round(min(traceable, 100), 1),
        format="score",
        category="C",
        detail=f"{vars.get('tasks_with_story', 0)}/{vars.get('tasks_total', 0)} tasks traced to stories",
    ))

    # Intake Staleness — count open items (simplified)
    stale = vars.get("intake_open", 0)
    results.append(KpiResult(
        name="Intake Staleness",
        value=stale,
        format="count",
        category="C",
        detail=f"{stale} items open",
        warning=stale > 5,
    ))

    # Archive Health — requires rollover tracking
    results.append(KpiResult(
        name="Archive Health",
        value=0.0,
        format="score",
        category="C",
        detail="Requires rollover history",
    ))

    # Coverage Gap
    gap_count = 0
    if docs_dir:
        expected = [
            "_project_status.md",
            "_project_roadmap.md",
            "_project_stories.md",
            "_project_tasks.md",
            "_intake_issues.md",
            "_intake_features.md",
        ]
        for fname in expected:
            if not (docs_dir / fname).exists():
                gap_count += 1
    results.append(KpiResult(
        name="Coverage Gap",
        value=gap_count,
        format="count",
        category="C",
        detail=f"{gap_count} missing files",
        warning=gap_count > 0,
    ))

    return results


def _compute_next_best_action(vars: dict) -> str:
    """Generate Next Best Action text recommendation."""
    if vars.get("tasks_blocked", 0) > 0:
        return f"Resolve {vars['tasks_blocked']} blocked task(s) first"
    if vars.get("tasks_reopened", 0) > 0:
        return f"Fix {vars['tasks_reopened']} reopened task(s) — rework before new work"
    if vars.get("intake_open", 0) > 5:
        return f"Triage backlog — {vars['intake_open']} intake items open"
    if vars.get("tasks_in_progress", 0) > 0:
        return f"Complete {vars['tasks_in_progress']} in-progress task(s)"
    if vars.get("tasks_open", 0) > 0:
        return f"Start highest-priority open task ({vars['tasks_open']} available)"
    return "All clear — consider planning next iteration"


# --- Custom KPIs ---


def compute_custom_kpis(
    custom_defs: list[dict], variables: dict[str, float]
) -> list[KpiResult]:
    """Evaluate custom TOML-defined KPIs."""
    results = []
    for defn in custom_defs:
        name = defn.get("name", "Unnamed")
        formula = defn.get("formula", "0")
        fmt = defn.get("format", "score")
        value_range = defn.get("range")
        warn_below = defn.get("warning_below")
        warn_above = defn.get("warning_above")

        value = evaluate_formula(formula, variables)

        # Clamp to range
        if value_range and len(value_range) == 2:
            value = max(value_range[0], min(value_range[1], value))

        # Check warnings
        warning = False
        if warn_below is not None and value < warn_below:
            warning = True
        if warn_above is not None and value > warn_above:
            warning = True

        results.append(KpiResult(
            name=name,
            value=round(value, 1),
            format=fmt,
            category="CUSTOM",
            detail=defn.get("description", ""),
            warning=warning,
        ))

    return results


# --- Plugin KPIs ---


def load_plugin_kpi(
    name: str,
    module_path: Path,
    variables: dict,
    docs_dir: Path,
) -> KpiResult:
    """Load and execute a Python plugin KPI.

    Plugin must have a compute(vars, docs_dir) function returning a dict
    with keys: value, format, detail, warning.
    """
    spec = importlib.util.spec_from_file_location("plugin_kpi", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    raw = module.compute(variables, docs_dir)

    return KpiResult(
        name=name,
        value=raw.get("value", 0),
        format=raw.get("format", "score"),
        category="PLUGIN",
        detail=raw.get("detail", ""),
        warning=raw.get("warning", False),
    )


# --- Aggregate ---


def compute_all_kpis(
    variables: dict[str, int | float],
    docs_dir: Path | None = None,
    custom_defs: list[dict] | None = None,
    plugin_defs: list[dict] | None = None,
) -> list[KpiResult]:
    """Compute all KPIs: built-in + custom + plugins."""
    results = compute_builtin_kpis(variables, docs_dir=docs_dir)

    if custom_defs:
        results.extend(compute_custom_kpis(custom_defs, variables))

    if plugin_defs and docs_dir:
        for pdef in plugin_defs:
            module_path = docs_dir.parent / pdef.get("module", "")
            if module_path.exists():
                result = load_plugin_kpi(
                    pdef.get("name", "Plugin"),
                    module_path,
                    variables,
                    docs_dir,
                )
                results.append(result)

    return results


# --- Dashboard ---


def format_dashboard(
    results: list[KpiResult],
    project_date: str = "",
) -> str:
    """Format KPI results as a terminal dashboard string."""
    lines = []
    sep = "=" * 72

    lines.append(sep)
    if project_date:
        lines.append(f"  DevLead — {project_date}")
    else:
        lines.append("  DevLead KPI Dashboard")
    lines.append(sep)

    # Group by category
    categories = {
        "A": "A. LLM EFFECTIVENESS",
        "B": "B. DELIVERY & PROJECT MANAGEMENT",
        "C": "C. PROJECT HEALTH",
        "CUSTOM": "CUSTOM (project-specific KPIs)",
        "PLUGIN": "PLUGIN KPIs",
    }

    for cat_key, cat_label in categories.items():
        cat_results = [r for r in results if r.category == cat_key]
        if not cat_results:
            continue

        lines.append("")
        lines.append(f"  {cat_label}")
        lines.append("  " + "-" * 64)

        for r in cat_results:
            warn_marker = " !!" if r.warning else ""
            value_str = _format_value(r)
            detail_str = f" | {r.detail}" if r.detail else ""
            lines.append(f"  {r.name:<22}| {value_str:<20}{detail_str}{warn_marker}")

    lines.append("")
    lines.append(sep)
    return "\n".join(lines)


def _format_value(r: KpiResult) -> str:
    """Format a KPI value based on its format type."""
    if r.format == "text":
        return "—"
    if r.format == "percent":
        return f"{r.value:.0f}%"
    if r.format == "count":
        return f"{r.value:.0f}"
    if r.format == "ratio":
        return f"{r.value:.2f}"
    if r.format == "days":
        return f"{r.value:.1f} days"
    # score
    return f"{r.value:.0f}/100"
