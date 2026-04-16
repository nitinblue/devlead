"""Tests for DevLead branded UI output."""
from devlead import ui


def test_banner_contains_brand():
    result = ui.banner()
    assert "DevLead" in result
    assert "v0.1.0" in result


def test_mini_contains_brand():
    result = ui.mini()
    assert "DevLead" in result


def test_ok_formats_message():
    result = ui.ok("test passed")
    assert "DevLead" in result
    assert "test passed" in result
    assert ui.ICON_OK in result


def test_fail_formats_message():
    result = ui.fail("something broke")
    assert "DevLead" in result
    assert "something broke" in result
    assert ui.ICON_FAIL in result


def test_warn_formats_message():
    result = ui.warn("be careful")
    assert "DevLead" in result
    assert "be careful" in result


def test_info_formats_message():
    result = ui.info("fyi")
    assert "DevLead" in result
    assert "fyi" in result


def test_gate_allowed():
    result = ui.gate_allowed("EXECUTE", "EXECUTE")
    assert "GATE EXECUTE" in result
    assert "EXECUTE" in result


def test_gate_blocked():
    result = ui.gate_blocked("EXECUTE", "ORIENT", ["EXECUTE", "UPDATE"])
    assert "BLOCKED" in result
    assert "ORIENT" in result


def test_state_transition():
    result = ui.state_transition("PLAN", "EXECUTE")
    assert "PLAN" in result
    assert "EXECUTE" in result


def test_session_start():
    result = ui.session_start()
    assert "DevLead" in result
    assert "ORIENT" in result
    assert "Session started" in result


def test_scope_active():
    result = ui.scope_active(["src/foo.py", "src/bar.py"])
    assert "2 paths" in result
    assert "src/foo.py" in result


def test_scope_clear():
    result = ui.scope_clear()
    assert "unlocked" in result


def test_checklist():
    result = ui.checklist({"item_a": True, "item_b": False})
    assert "item_a" in result
    assert "item_b" in result
    assert ui.ICON_OK in result
    assert ui.ICON_CIRCLE in result


def test_section_header():
    result = ui.section("My Section")
    assert "My Section" in result


def test_kv_pair():
    result = ui.kv("key", "value")
    assert "key:" in result
    assert "value" in result


def test_hook_msg_plain_text():
    result = ui.hook_msg("gate passed")
    assert result == "[DevLead] gate passed"
    # No ANSI codes in hook messages
    assert "\033[" not in result


def test_hook_err_branded():
    result = ui.hook_err("blocked")
    assert "[DevLead]" in result
    assert "blocked" in result
