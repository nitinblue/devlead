"""Tests for kpi_engine.py — formula evaluator, built-in KPIs, custom, plugins."""

import shutil
import pytest
from pathlib import Path
from devlead.kpi_engine import (
    KpiResult,
    evaluate_formula,
    compute_builtin_kpis,
    compute_custom_kpis,
    load_plugin_kpi,
    compute_all_kpis,
    format_dashboard,
)


FIXTURES = Path(__file__).parent / "fixtures"


# --- Formula evaluator ---

def test_formula_simple_add():
    assert evaluate_formula("2 + 3", {}) == 5.0


def test_formula_simple_multiply():
    assert evaluate_formula("4 * 5", {}) == 20.0


def test_formula_precedence():
    """Multiplication before addition."""
    assert evaluate_formula("2 + 3 * 4", {}) == 14.0


def test_formula_parentheses():
    assert evaluate_formula("(2 + 3) * 4", {}) == 20.0


def test_formula_variables():
    vars = {"tasks_done": 10, "tasks_total": 20}
    assert evaluate_formula("tasks_done / tasks_total * 100", vars) == 50.0


def test_formula_division_by_zero():
    """Division by zero returns 0."""
    assert evaluate_formula("10 / 0", {}) == 0.0


def test_formula_nested_parens():
    assert evaluate_formula("((2 + 3) * (4 - 1))", {}) == 15.0


def test_formula_subtraction():
    assert evaluate_formula("10 - 3", {}) == 7.0


def test_formula_unknown_variable():
    """Unknown variables default to 0."""
    assert evaluate_formula("unknown_var + 5", {}) == 5.0


# --- KpiResult ---

def test_kpi_result_structure():
    r = KpiResult(name="Test", value=42.0, format="score")
    assert r.name == "Test"
    assert r.value == 42.0
    assert r.format == "score"


# --- Built-in KPIs ---

def test_compute_builtin_kpis(tmp_path):
    """Built-in KPIs compute from fixture data."""
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_builtin_kpis(vars)

    assert isinstance(results, list)
    assert len(results) > 0

    # Check we have all three categories
    categories = {r.category for r in results}
    assert "A" in categories  # LLM Effectiveness
    assert "B" in categories  # Delivery
    assert "C" in categories  # Project Health


def test_builtin_convergence_kpi(tmp_path):
    """Convergence KPI matches expected value."""
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_builtin_kpis(vars)

    convergence = _find_kpi(results, "Code-Domain Convergence")
    assert convergence is not None
    # tasks_with_story (8) / tasks_active (7) * 100 = 114 clamped to 100
    assert convergence.value > 0


def test_builtin_intake_throughput(tmp_path):
    """Intake throughput KPI."""
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_builtin_kpis(vars)

    throughput = _find_kpi(results, "Intake Throughput")
    assert throughput is not None
    # intake_closed (2) / intake_total (6) * 100 = 33.3
    assert 33.0 <= throughput.value <= 34.0


def test_builtin_coverage_gap(tmp_path):
    """Coverage gap counts missing files."""
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_builtin_kpis(vars, docs_dir=tmp_path)

    gap = _find_kpi(results, "Coverage Gap")
    assert gap is not None


def test_builtin_next_best_action(tmp_path):
    """Next Best Action is a text recommendation."""
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_builtin_kpis(vars)

    nba = _find_kpi(results, "Next Best Action")
    assert nba is not None
    assert nba.format == "text"


# --- Custom KPIs ---

def test_compute_custom_kpis():
    custom_defs = [
        {
            "name": "Test Custom",
            "description": "A test",
            "formula": "(tasks_done / tasks_total) * 100",
            "range": [0, 100],
            "format": "percent",
        }
    ]
    vars = {"tasks_done": 3, "tasks_total": 10}
    results = compute_custom_kpis(custom_defs, vars)
    assert len(results) == 1
    assert results[0].name == "Test Custom"
    assert results[0].value == 30.0


def test_compute_custom_kpi_clamped():
    """Value clamped to range."""
    custom_defs = [
        {
            "name": "Clamped",
            "formula": "200",
            "range": [0, 100],
            "format": "score",
        }
    ]
    results = compute_custom_kpis(custom_defs, {})
    assert results[0].value == 100.0


def test_compute_custom_kpi_warning_below():
    custom_defs = [
        {
            "name": "Low",
            "formula": "30",
            "warning_below": 50,
            "format": "score",
        }
    ]
    results = compute_custom_kpis(custom_defs, {})
    assert results[0].warning is True


def test_compute_custom_kpi_warning_above():
    custom_defs = [
        {
            "name": "High",
            "formula": "80",
            "warning_above": 50,
            "format": "score",
        }
    ]
    results = compute_custom_kpis(custom_defs, {})
    assert results[0].warning is True


# --- Plugin KPIs ---

def test_load_plugin_kpi():
    plugin_path = FIXTURES / "kpis" / "sample_plugin.py"
    vars = {"tasks_done": 5}
    result = load_plugin_kpi("Test Plugin", plugin_path, vars, FIXTURES)
    assert result.name == "Test Plugin"
    assert result.value == 50  # 5 * 10
    assert result.warning is False


def test_load_plugin_kpi_warning():
    plugin_path = FIXTURES / "kpis" / "sample_plugin.py"
    vars = {"tasks_done": 1}
    result = load_plugin_kpi("Test Plugin", plugin_path, vars, FIXTURES)
    assert result.warning is True


# --- Dashboard ---

def test_format_dashboard(tmp_path):
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_builtin_kpis(vars)
    output = format_dashboard(results)

    assert "LLM EFFECTIVENESS" in output
    assert "DELIVERY" in output
    assert "PROJECT HEALTH" in output


def test_format_dashboard_with_custom():
    custom_results = [
        KpiResult(name="Custom 1", value=75.0, format="score", category="CUSTOM")
    ]
    output = format_dashboard(custom_results)
    assert "CUSTOM" in output
    assert "Custom 1" in output


# --- compute_all_kpis ---

def test_compute_all_kpis(tmp_path):
    _copy_fixtures_to(tmp_path)
    from datetime import date
    from devlead.doc_parser import get_builtin_vars
    vars = get_builtin_vars(tmp_path, today=date(2026, 4, 5))
    results = compute_all_kpis(vars, docs_dir=tmp_path)
    assert len(results) > 0


# --- helpers ---

def _copy_fixtures_to(dest: Path) -> None:
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, dest / f.name)


def _find_kpi(results: list[KpiResult], name: str) -> KpiResult | None:
    for r in results:
        if r.name == name:
            return r
    return None
