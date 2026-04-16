"""Tests for gate_engine.py — configurable gate rule evaluation."""

import pytest
from devlead.gate_engine import evaluate_gates, match_condition, match_path


# --- match_path ---

def test_match_path_exact():
    assert match_path("src/main.py", "src/main.py")

def test_match_path_glob_star():
    assert match_path("src/*.py", "src/main.py")

def test_match_path_double_star():
    assert match_path("**/memory/**", "/home/user/.claude/projects/test/memory/note.md")

def test_match_path_double_star_devlead_docs():
    assert match_path("**/devlead_docs/**", "/c/Users/nitin/project/devlead_docs/_tasks.md")

def test_match_path_no_match():
    assert not match_path("**/memory/**", "/home/user/src/main.py")

def test_match_path_normalizes_backslashes():
    assert match_path("**/memory/**", "C:\\Users\\nitin\\.claude\\projects\\test\\memory\\note.md")

def test_match_path_claude_memory_pattern():
    assert match_path("**/.claude/*/memory/**", "/home/user/.claude/projects/test/memory/note.md")

def test_match_path_claude_memory_windows():
    assert match_path("**/.claude/*/memory/**", "C:\\Users\\nitin\\.claude\\projects\\hash123\\memory\\file.md")


# --- match_condition ---

def test_condition_always():
    assert match_condition("always", {})

def test_condition_state_not_in_true():
    assert match_condition("state_not_in(UPDATE, SESSION_END)", {"current_state": "EXECUTE"})

def test_condition_state_not_in_false():
    assert not match_condition("state_not_in(UPDATE, SESSION_END)", {"current_state": "UPDATE"})

def test_condition_state_in_true():
    assert match_condition("state_in(EXECUTE, UPDATE)", {"current_state": "EXECUTE"})

def test_condition_state_in_false():
    assert not match_condition("state_in(EXECUTE, UPDATE)", {"current_state": "ORIENT"})

def test_condition_no_active_task_true():
    assert match_condition("no_active_task", {"has_active_task": False})

def test_condition_no_active_task_false():
    assert not match_condition("no_active_task", {"has_active_task": True})

def test_condition_unknown():
    assert not match_condition("bogus_condition", {"current_state": "EXECUTE"})

def test_condition_whitespace():
    assert match_condition("  always  ", {})


# --- evaluate_gates ---

def test_evaluate_no_rules():
    action, msg = evaluate_gates([], {"tool_name": "Edit", "file_path": "src/main.py"})
    assert action == "allow"
    assert msg == ""

def test_evaluate_first_match_wins():
    gates = [
        {"name": "first", "trigger": "Edit|Write", "condition": "always", "action": "block", "message": "blocked"},
        {"name": "second", "trigger": "Edit|Write", "condition": "always", "action": "warn", "message": "warned"},
    ]
    action, msg = evaluate_gates(gates, {"tool_name": "Edit", "file_path": "x.py", "current_state": "EXECUTE"})
    assert action == "block"
    assert msg == "blocked"

def test_evaluate_trigger_mismatch_skips():
    gates = [
        {"name": "bash-only", "trigger": "Bash", "condition": "always", "action": "block", "message": "no bash"},
    ]
    action, msg = evaluate_gates(gates, {"tool_name": "Edit", "file_path": "x.py"})
    assert action == "allow"

def test_evaluate_path_filter():
    gates = [
        {"name": "docs", "trigger": "Edit|Write", "path": "**/devlead_docs/**", "condition": "always", "action": "warn", "message": "docs"},
    ]
    # Matches
    action, msg = evaluate_gates(gates, {"tool_name": "Write", "file_path": "/project/devlead_docs/_tasks.md", "current_state": "EXECUTE"})
    assert action == "warn"
    # Doesn't match
    action, msg = evaluate_gates(gates, {"tool_name": "Write", "file_path": "/project/src/main.py", "current_state": "EXECUTE"})
    assert action == "allow"

def test_evaluate_condition_filter():
    gates = [
        {"name": "memory", "trigger": "Edit|Write", "path": "**/.claude/*/memory/**", "condition": "state_not_in(UPDATE, SESSION_END)", "action": "block", "message": "memory blocked"},
    ]
    # In EXECUTE → blocked
    ctx = {"tool_name": "Write", "file_path": "/home/.claude/proj/memory/note.md", "current_state": "EXECUTE"}
    action, msg = evaluate_gates(gates, ctx)
    assert action == "block"
    # In UPDATE → no match → allow
    ctx["current_state"] = "UPDATE"
    action, msg = evaluate_gates(gates, ctx)
    assert action == "allow"

def test_evaluate_memory_and_docs_defaults():
    """Test the two default gate rules that DevLead ships with."""
    gates = [
        {"name": "memory-from-docs", "trigger": "Edit|Write", "path": "**/.claude/*/memory/**", "condition": "state_not_in(UPDATE, SESSION_END)", "action": "block", "message": "Memory must derive from devlead_docs."},
        {"name": "protect-docs", "trigger": "Edit|Write", "path": "**/devlead_docs/**", "condition": "state_not_in(UPDATE, SESSION_END)", "action": "warn", "message": "Editing devlead_docs outside UPDATE."},
    ]
    # Memory write in EXECUTE → block
    action, _ = evaluate_gates(gates, {"tool_name": "Write", "file_path": "/home/.claude/proj/memory/x.md", "current_state": "EXECUTE"})
    assert action == "block"
    # Docs write in ORIENT → warn
    action, _ = evaluate_gates(gates, {"tool_name": "Edit", "file_path": "/proj/devlead_docs/_tasks.md", "current_state": "ORIENT"})
    assert action == "warn"
    # Normal file in any state → allow
    action, _ = evaluate_gates(gates, {"tool_name": "Edit", "file_path": "/proj/src/main.py", "current_state": "ORIENT"})
    assert action == "allow"
    # Memory write in UPDATE → allow
    action, _ = evaluate_gates(gates, {"tool_name": "Write", "file_path": "/home/.claude/proj/memory/x.md", "current_state": "UPDATE"})
    assert action == "allow"

def test_evaluate_no_path_matches_all_files():
    """Gate without path field matches any file."""
    gates = [
        {"name": "no-task", "trigger": "Edit|Write", "condition": "no_active_task", "action": "warn", "message": "no task"},
    ]
    action, _ = evaluate_gates(gates, {"tool_name": "Edit", "file_path": "any.py", "has_active_task": False})
    assert action == "warn"
    action, _ = evaluate_gates(gates, {"tool_name": "Edit", "file_path": "any.py", "has_active_task": True})
    assert action == "allow"
