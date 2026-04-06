"""DevLead View — Option B workbook format.

Uses the shared workbook data model. Each TBO is a self-contained block
with summary line + Story→Task table. Shadow work at bottom.
"""

from pathlib import Path

from devlead import ui
from devlead.workbook import load_workbook, Workbook, TBO, Story, Task


def _status_color(status: str) -> str:
    s = status.upper()
    if "DONE" in s or "COMPLETE" in s or "ACCEPT" in s:
        return ui.GREEN
    if "IN_PROGRESS" in s:
        return ui.YELLOW
    if "BLOCKED" in s or "SHADOW" in s:
        return ui.RED
    return ui.DIM


def _status_icon(status: str) -> str:
    s = status.upper()
    if "DONE" in s or "COMPLETE" in s:
        return ui.ICON_OK
    if "IN_PROGRESS" in s:
        return ui.ICON_ARROW
    if "BLOCKED" in s:
        return ui.ICON_FAIL
    return " "


def _type_label(task_type: str) -> str:
    colors = {"F": ui.GREEN, "NF": ui.CYAN, "SHADOW": ui.RED}
    c = colors.get(task_type, ui.DIM)
    return f"{c}{task_type}{ui.RESET}"


def _tbo_status_color(tbo: TBO) -> str:
    s = tbo.status.upper()
    if "DONE" in s:
        return ui.GREEN
    if "ACCEPT" in s:
        return ui.YELLOW
    if "IN_PROGRESS" in s or tbo.stories_done > 0:
        return ui.YELLOW
    if "NOT" in s:
        return ui.DIM
    return ui.DIM


def _render_tbo(tbo: TBO) -> list[str]:
    """Render a single TBO block in Option B format."""
    lines: list[str] = []
    c = _tbo_status_color(tbo)

    # TBO header
    lines.append(
        f"{ui.BRIGHT_CYAN}{ui.LINE_H * 3}{ui.RESET} "
        f"{ui.BOLD}{c}{tbo.id}: {tbo.objective}{ui.RESET} "
        f"{ui.GRAY}[{tbo.status}]{ui.RESET}"
    )

    # Planned/Actual dates
    dates = []
    if tbo.planned and tbo.planned != "—":
        dates.append(f"Planned: {tbo.planned}")
    if tbo.actual and tbo.actual != "—":
        dates.append(f"Actual: {tbo.actual}")
    if dates:
        lines.append(f"    {ui.DIM}{' | '.join(dates)}{ui.RESET}")

    # Summary line
    shadow = sum(1 for s in tbo.stories for t in s.tasks if t.task_type == "SHADOW")
    lines.append(
        f"    {ui.DIM}Stories:{ui.RESET} {tbo.stories_done}/{tbo.stories_total} done"
        f" {ui.GRAY}|{ui.RESET} "
        f"{ui.DIM}Tasks:{ui.RESET} {tbo.tasks_done}/{tbo.tasks_total} done"
        f" {ui.GRAY}|{ui.RESET} "
        f"{ui.DIM}Shadow:{ui.RESET} {shadow}"
    )
    lines.append("")

    if not tbo.stories:
        lines.append(f"    {ui.DIM}(no stories linked — needs breakdown){ui.RESET}")
        lines.append("")
        return lines

    # Table header
    lines.append(
        f"    {ui.DIM}Story        {ui.LINE_V} Task         "
        f"{ui.LINE_V} Description                    "
        f"{ui.LINE_V} Status      {ui.LINE_V} Type{ui.RESET}"
    )
    lines.append(
        f"    {ui.DIM}{ui.LINE_H * 13}{ui.LINE_V}{ui.LINE_H * 14}"
        f"{ui.LINE_V}{ui.LINE_H * 32}"
        f"{ui.LINE_V}{ui.LINE_H * 13}{ui.LINE_V}{ui.LINE_H * 5}{ui.RESET}"
    )

    for story in tbo.stories:
        sc = _status_color(story.status)
        icon = _status_icon(story.status)
        desc = story.description[:30]
        lines.append(
            f"    {sc}{story.id:<13}{ui.RESET}{ui.GRAY}{ui.LINE_V}{ui.RESET}"
            f" {'':13}{ui.GRAY}{ui.LINE_V}{ui.RESET}"
            f" {sc}{desc:<30}{ui.RESET}"
            f" {ui.GRAY}{ui.LINE_V}{ui.RESET}"
            f" {sc}{icon} {story.status:<10}{ui.RESET}"
            f" {ui.GRAY}{ui.LINE_V}{ui.RESET}"
            f" {ui.DIM}--{ui.RESET}"
        )
        for task in story.tasks:
            tc = _status_color(task.status)
            ticon = _status_icon(task.status)
            tdesc = task.description[:30]
            lines.append(
                f"    {'':13}{ui.GRAY}{ui.LINE_V}{ui.RESET}"
                f" {tc}{task.id:<13}{ui.RESET}{ui.GRAY}{ui.LINE_V}{ui.RESET}"
                f" {tc}{tdesc:<30}{ui.RESET}"
                f" {ui.GRAY}{ui.LINE_V}{ui.RESET}"
                f" {tc}{ticon} {task.status:<10}{ui.RESET}"
                f" {ui.GRAY}{ui.LINE_V}{ui.RESET}"
                f" {_type_label(task.task_type)}"
            )

    lines.append("")
    return lines


def generate_project_view(docs_dir: Path) -> str:
    """Build the full workbook view using Option B format."""
    wb = load_workbook(docs_dir)

    lines: list[str] = []
    lines.append(ui.banner())
    lines.append(ui.section("DevLead Workbook"))

    # Convergence
    done = sum(1 for t in wb.tbos if "DONE" in t.status.upper())
    total = len(wb.tbos)
    pct = f"{done}/{total}" if total else "0/0"
    lines.append(f"\n  {ui.DIM}Convergence:{ui.RESET} {ui.BOLD}{pct} TBOs{ui.RESET}")
    lines.append("")

    # Each TBO block
    for tbo in wb.tbos:
        lines.extend(_render_tbo(tbo))

    # Shadow work
    if wb.shadow_tasks:
        lines.append(
            f"{ui.BRIGHT_CYAN}{ui.LINE_H * 3}{ui.RESET} "
            f"{ui.BOLD}{ui.RED}SHADOW WORK{ui.RESET} "
            f"{ui.GRAY}({len(wb.shadow_tasks)} items){ui.RESET}"
        )
        for t in wb.shadow_tasks:
            tc = _status_color(t.status)
            lines.append(
                f"    {ui.RED}{t.id}{ui.RESET} "
                f"{tc}{t.description[:40]}{ui.RESET} "
                f"[{t.status}] {_type_label(t.task_type)}"
            )
        lines.append("")
    else:
        lines.append(ui.ok("No shadow work detected."))
        lines.append("")

    # Summary
    lines.append(
        f"{ui.DIM}{total} TBOs {ui.LINE_V} "
        f"{wb.total_stories} stories {ui.LINE_V} "
        f"{wb.total_tasks} tasks {ui.LINE_V} "
        f"{len(wb.shadow_tasks)} shadow{ui.RESET}"
    )

    return "\n".join(lines)
