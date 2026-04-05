"""Tests for config.py — devlead.toml parsing with defaults."""

import pytest
from pathlib import Path
from devlead.config import (
    DEFAULT_CONFIG,
    load_config,
    get_docs_dir,
    get_state_file,
    get_kpi_thresholds,
    get_custom_kpis,
    get_rollover_config,
    get_hook_config,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_default_config_structure():
    """DEFAULT_CONFIG has all required sections."""
    assert "project" in DEFAULT_CONFIG
    assert "kpis" in DEFAULT_CONFIG
    assert "rollover" in DEFAULT_CONFIG
    assert "hooks" in DEFAULT_CONFIG


def test_default_config_values():
    """Default values match spec."""
    assert DEFAULT_CONFIG["project"]["docs_dir"] == "claude_docs"
    assert DEFAULT_CONFIG["kpis"]["circles_warning"] == 50
    assert DEFAULT_CONFIG["kpis"]["ftr_minimum"] == 60
    assert DEFAULT_CONFIG["kpis"]["convergence_target"] == 80
    assert DEFAULT_CONFIG["rollover"]["day_of_month"] == 1


def test_load_config_no_toml(tmp_path):
    """When no devlead.toml exists, returns defaults."""
    config = load_config(tmp_path)
    assert config["project"]["docs_dir"] == "claude_docs"
    assert config["kpis"]["circles_warning"] == 50


def test_load_config_with_toml():
    """Loading sample toml merges with defaults."""
    # Create a temp dir with the sample toml
    config = load_config(FIXTURES, config_name="sample_devlead.toml")
    assert config["project"]["name"] == "test-project"
    assert config["project"]["docs_dir"] == "my_docs"


def test_load_config_overrides_defaults():
    """TOML values override defaults."""
    config = load_config(FIXTURES, config_name="sample_devlead.toml")
    assert config["kpis"]["circles_warning"] == 40
    assert config["kpis"]["ftr_minimum"] == 70
    assert config["kpis"]["convergence_target"] == 90


def test_load_config_preserves_defaults_for_missing():
    """Keys not in TOML keep their default values."""
    config = load_config(FIXTURES, config_name="sample_devlead.toml")
    # rollover.retain_months is in the toml as 6
    assert config["rollover"]["retain_months"] == 6
    # hooks.gate_plan_mode is false in toml
    assert config["hooks"]["gate_plan_mode"] is False


def test_get_docs_dir(tmp_path):
    """get_docs_dir returns resolved path."""
    config = load_config(tmp_path)
    docs = get_docs_dir(config, tmp_path)
    assert docs == tmp_path / "claude_docs"


def test_get_docs_dir_custom():
    """get_docs_dir respects custom docs_dir."""
    config = load_config(FIXTURES, config_name="sample_devlead.toml")
    docs = get_docs_dir(config, FIXTURES)
    assert docs == FIXTURES / "my_docs"


def test_get_state_file(tmp_path):
    """get_state_file returns path inside docs_dir."""
    config = load_config(tmp_path)
    sf = get_state_file(config, tmp_path)
    assert sf == tmp_path / "claude_docs" / "session_state.json"


def test_get_kpi_thresholds(tmp_path):
    """get_kpi_thresholds returns threshold dict."""
    config = load_config(tmp_path)
    thresholds = get_kpi_thresholds(config)
    assert thresholds["circles_warning"] == 50
    assert thresholds["ftr_minimum"] == 60
    assert thresholds["convergence_target"] == 80


def test_get_custom_kpis_none(tmp_path):
    """No custom KPIs when toml has none."""
    config = load_config(tmp_path)
    custom = get_custom_kpis(config)
    assert custom == []


def test_get_custom_kpis_from_toml():
    """Custom KPIs parsed from sample toml."""
    config = load_config(FIXTURES, config_name="sample_devlead.toml")
    custom = get_custom_kpis(config)
    assert len(custom) == 1
    assert custom[0]["name"] == "Test KPI"
    assert custom[0]["formula"] == "(tasks_done / tasks_total) * 100"


def test_get_rollover_config(tmp_path):
    """Rollover config from defaults."""
    config = load_config(tmp_path)
    rollover = get_rollover_config(config)
    assert rollover["day_of_month"] == 1
    assert isinstance(rollover["files"], list)


def test_get_rollover_config_custom():
    """Rollover config from sample toml."""
    config = load_config(FIXTURES, config_name="sample_devlead.toml")
    rollover = get_rollover_config(config)
    assert rollover["day_of_month"] == 15
    assert rollover["retain_months"] == 6
    assert len(rollover["files"]) == 2


def test_get_hook_config(tmp_path):
    """Hook config from defaults."""
    config = load_config(tmp_path)
    hooks = get_hook_config(config)
    assert hooks["session_start"] is True
    assert hooks["gate_edits"] is True
