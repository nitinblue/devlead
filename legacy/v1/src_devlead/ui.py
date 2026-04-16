"""DevLead UI — branded terminal output with ANSI colors.

Every DevLead action should be visually attributable to DevLead,
not confused with model-initiated actions.

Handles Windows cp1252 terminals gracefully with ASCII fallbacks.
"""
import sys

# ANSI escape codes — stdlib only, no dependencies
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Brand colors
CYAN = "\033[36m"
BRIGHT_CYAN = "\033[96m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
WHITE = "\033[97m"
GRAY = "\033[90m"

# Detect Unicode support — Windows cp1252 can't handle box-drawing
_UNICODE = getattr(sys.stdout, "encoding", "") or ""
_CAN_UNICODE = _UNICODE.lower().replace("-", "") in (
    "utf8", "utf16", "utf32", "utf8sig",
) or _UNICODE.lower().startswith("utf")

# Box-drawing with ASCII fallbacks
if _CAN_UNICODE:
    BOX_TL, BOX_TR, BOX_BL, BOX_BR = "╔", "╗", "╚", "╝"
    BOX_H, BOX_V = "═", "║"
    LINE_H, LINE_V = "─", "│"
    ICON_BRAND = "⚡"
    ICON_OK, ICON_FAIL, ICON_WARN, ICON_INFO = "✓", "✗", "⚠", "ℹ"
    ICON_BULLET = "•"
    ICON_CIRCLE = "○"
    ICON_ARROW = "→"
else:
    BOX_TL, BOX_TR, BOX_BL, BOX_BR = "+", "+", "+", "+"
    BOX_H, BOX_V = "=", "|"
    LINE_H, LINE_V = "-", "|"
    ICON_BRAND = "*"
    ICON_OK, ICON_FAIL, ICON_WARN, ICON_INFO = "+", "x", "!", "i"
    ICON_BULLET = "*"
    ICON_CIRCLE = "o"
    ICON_ARROW = "->"

BRAND = "DevLead"


def _version() -> str:
    from devlead import __version__
    return __version__


# --- Brand elements ---


def banner() -> str:
    """Full branded banner for CLI commands."""
    ver = _version()
    tag = f"{ICON_BRAND} DevLead"
    tagline = "Lead your development. Don't let AI wander."
    inner_w = max(len(tag) + len(ver) + 4, len(tagline) + 4)
    pad1 = inner_w - len(tag) - len(ver) - 3
    pad2 = inner_w - len(tagline) - 2
    return (
        f"\n{BRIGHT_CYAN}{BOX_TL}{BOX_H * inner_w}{BOX_TR}{RESET}\n"
        f"{BRIGHT_CYAN}{BOX_V}{RESET}"
        f"  {BOLD}{BRIGHT_CYAN}{tag}{RESET}"
        f"  {DIM}v{ver}{RESET}"
        f"{' ' * pad1}"
        f"{BRIGHT_CYAN}{BOX_V}{RESET}\n"
        f"{BRIGHT_CYAN}{BOX_V}{RESET}"
        f"  {DIM}{tagline}{RESET}"
        f"{' ' * pad2}"
        f"{BRIGHT_CYAN}{BOX_V}{RESET}\n"
        f"{BRIGHT_CYAN}{BOX_BL}{BOX_H * inner_w}{BOX_BR}{RESET}"
    )


def mini() -> str:
    """Compact one-line brand prefix."""
    return f"{BOLD}{BRIGHT_CYAN}{ICON_BRAND} DevLead{RESET} {GRAY}{LINE_V}{RESET}"


# --- Formatted messages ---


def ok(message: str) -> str:
    return f"{mini()} {GREEN}{ICON_OK}{RESET} {message}"


def fail(message: str) -> str:
    return f"{mini()} {RED}{ICON_FAIL}{RESET} {message}"


def warn(message: str) -> str:
    return f"{mini()} {YELLOW}{ICON_WARN}{RESET} {message}"


def info(message: str) -> str:
    return f"{mini()} {CYAN}{ICON_INFO}{RESET} {message}"


# --- State machine formatting ---


def gate_allowed(gate_name: str, state: str) -> str:
    return (
        f"{mini()} {GREEN}{ICON_OK} GATE {gate_name}{RESET}"
        f" {GRAY}[{state}]{RESET}"
    )


def gate_blocked(gate_name: str, state: str, allowed: list[str]) -> str:
    return (
        f"{mini()} {RED}{ICON_FAIL} GATE {gate_name} BLOCKED{RESET}"
        f" {GRAY}[{state}]{RESET}"
        f" {DIM}requires {allowed}{RESET}"
    )


def state_transition(from_s: str, to_s: str) -> str:
    return (
        f"{mini()} {MAGENTA}{ICON_ARROW}{RESET}"
        f" {WHITE}{from_s}{RESET} {ICON_ARROW} {BOLD}{GREEN}{to_s}{RESET}"
    )


def session_start() -> str:
    return (
        f"\n{banner()}\n"
        f"{mini()} {GREEN}Session started{RESET}"
        f" {GRAY}{LINE_V}{RESET} State: {BOLD}ORIENT{RESET}\n"
        f"{mini()} {DIM}Read docs, scan intake, report KPIs{RESET}"
    )


# --- Scope ---


def scope_active(paths: list[str]) -> str:
    lines = [f"{mini()} {CYAN}Scope lock active{RESET} ({len(paths)} paths):"]
    for p in paths:
        lines.append(f"  {GREEN}{ICON_BULLET}{RESET} {p}")
    return "\n".join(lines)


def scope_clear() -> str:
    return f"{mini()} {DIM}Scope: unlocked{RESET}"


# --- Checklist ---


def checklist(items: dict[str, bool]) -> str:
    lines = []
    for key, done in items.items():
        mark = f"{GREEN}{ICON_OK}{RESET}" if done else f"{RED}{ICON_CIRCLE}{RESET}"
        lines.append(f"  {mark} {key}")
    return "\n".join(lines)


# --- Section headers ---


def section(title: str) -> str:
    pad = max(0, 38 - len(title))
    return f"\n{BRIGHT_CYAN}{LINE_H * 3}{RESET} {BOLD}{title}{RESET} {BRIGHT_CYAN}{LINE_H * pad}{RESET}"


def kv(key: str, value: str) -> str:
    return f"  {DIM}{key}:{RESET} {value}"


# --- Hook messages (plain text for JSON systemMessage) ---


def hook_msg(message: str) -> str:
    """Plain-text branded prefix for hook systemMessages.
    Goes into JSON consumed by the model — no ANSI, no Unicode.
    """
    return f"[DevLead] {message}"


def hook_err(message: str) -> str:
    """Branded prefix for hook stderr (block messages).
    Uses ANSI but no Unicode for Windows compatibility.
    """
    return f"{BOLD}{RED}[DevLead]{RESET} {message}"
