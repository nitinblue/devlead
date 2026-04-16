"""Configurable gate engine for DevLead.

Evaluates user-defined gate rules from devlead.toml [[gates]] entries.
Rules are evaluated in order — first match wins.
"""
from fnmatch import fnmatch


def evaluate_gates(gates: list[dict], context: dict) -> tuple[str, str]:
    """Evaluate gate rules against context. Returns (action, message) of first match.

    context keys:
        tool_name: str — the tool being used (e.g., "Edit", "Write")
        file_path: str — normalized file path (forward slashes)
        current_state: str — current DevLead state
        has_active_task: bool — whether an IN_PROGRESS task exists

    Returns ("allow", "") if no rule matches.
    """
    for rule in gates:
        if not _matches_trigger(rule.get("trigger", ""), context.get("tool_name", "")):
            continue
        if "path" in rule and rule["path"] and not match_path(rule["path"], context.get("file_path", "")):
            continue
        if not match_condition(rule.get("condition", "always"), context):
            continue
        return rule.get("action", "log"), rule.get("message", f"Gate '{rule.get('name', 'unnamed')}' triggered.")
    return "allow", ""


def _matches_trigger(trigger: str, tool_name: str) -> bool:
    """Check if tool_name matches the trigger pattern (pipe-separated)."""
    if not trigger:
        return True
    return tool_name in trigger.split("|")


def match_condition(condition: str, context: dict) -> bool:
    """Evaluate a condition string against context.

    Supported:
        state_not_in(S1, S2, ...) — true if current_state not in list
        state_in(S1, S2, ...) — true if current_state in list
        no_active_task — true if has_active_task is False
        always — always true
    """
    condition = condition.strip()
    if condition == "always":
        return True
    if condition == "no_active_task":
        return not context.get("has_active_task", False)
    if condition.startswith("state_not_in(") and condition.endswith(")"):
        states = _parse_state_list(condition[13:-1])
        return context.get("current_state", "") not in states
    if condition.startswith("state_in(") and condition.endswith(")"):
        states = _parse_state_list(condition[9:-1])
        return context.get("current_state", "") in states
    return False  # unknown condition = no match


def _parse_state_list(raw: str) -> list[str]:
    """Parse comma-separated state names, stripping whitespace."""
    return [s.strip() for s in raw.split(",") if s.strip()]


def match_path(pattern: str, file_path: str) -> bool:
    """Glob-style path matching. Normalizes to forward slashes."""
    norm = file_path.replace("\\", "/")
    pat = pattern.replace("\\", "/")
    # Try direct fnmatch
    if fnmatch(norm, pat):
        return True
    # Also try matching against just the tail if pattern starts with **
    if pat.startswith("**/"):
        # Match against any suffix
        suffix_pat = pat[3:]
        parts = norm.split("/")
        for i in range(len(parts)):
            candidate = "/".join(parts[i:])
            if fnmatch(candidate, suffix_pat):
                return True
    return False
