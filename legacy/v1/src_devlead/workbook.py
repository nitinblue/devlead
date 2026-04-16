"""Workbook — shared data model for TBO→Story→Task hierarchy.

Single source of truth for both terminal (view.py) and HTML (dashboard.py)
renderers. Reads devlead_docs markdown tables and builds a typed hierarchy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import re

from devlead.doc_parser import _read_if_exists, parse_table


# ── Data classes ──────────────────────────────────────────────


@dataclass
class Task:
    id: str  # TASK-001
    description: str
    story_id: str  # S-001, E-001, or "—"
    priority: str  # P1, P2, P3
    status: str  # DONE, IN_PROGRESS, OPEN, BLOCKED, ON_HOLD
    task_type: str  # F, NF, SHADOW
    assignee: str
    total_tokens: int = 0
    session_count: int = 0
    duration_min: int = 0


@dataclass
class Story:
    id: str  # S-001
    description: str
    epic_id: str  # E-001
    tbo_ids: list[str] = field(default_factory=list)
    status: str = ""
    dod: str = ""
    tasks: list[Task] = field(default_factory=list)
    total_tokens: int = 0
    session_count: int = 0
    duration_min: int = 0
    weight: int = 0  # out of 100 for its TBO


@dataclass
class TBO:
    id: str  # TBO-1
    objective: str
    status: str  # NOT_STARTED, IN_PROGRESS, ACCEPTANCE, DONE
    planned: str = ""
    actual: str = ""
    metric: str = ""
    weight: int = 0  # out of 100 for its BO
    dod: str = ""  # Definition of Done
    stories: list[Story] = field(default_factory=list)

    @property
    def stories_done(self) -> int:
        return sum(1 for s in self.stories if "DONE" in s.status.upper())

    @property
    def stories_total(self) -> int:
        return len(self.stories)

    @property
    def tasks_done(self) -> int:
        return sum(
            1 for s in self.stories for t in s.tasks if "DONE" in t.status.upper()
        )

    @property
    def tasks_total(self) -> int:
        return sum(len(s.tasks) for s in self.stories)


@dataclass
class BO:
    """Business Objective — phase-scoped, frozen when accepted."""
    id: str
    objective: str
    weight: int  # out of 100 for the phase
    status: str  # DRAFT, FROZEN, DONE
    phase: str
    tbos: list[TBO] = field(default_factory=list)


@dataclass
class Workbook:
    bos: list[BO] = field(default_factory=list)
    tbos: list[TBO] = field(default_factory=list)
    shadow_tasks: list[Task] = field(default_factory=list)

    @property
    def convergence(self) -> float:
        total = len(self.tbos)
        if total == 0:
            return 0.0
        done = sum(1 for t in self.tbos if "DONE" in t.status.upper())
        return done / total

    @property
    def total_stories(self) -> int:
        return sum(t.stories_total for t in self.tbos)

    @property
    def total_tasks(self) -> int:
        shadow = len(self.shadow_tasks)
        linked = sum(t.tasks_total for t in self.tbos)
        return linked + shadow


# ── Loader ────────────────────────────────────────────────────


def _parse_linked_ids(cell: str) -> list[str]:
    """Split comma-separated IDs like 'TBO-1, TBO-3' into a list."""
    if not cell or cell.strip() == "—":
        return []
    return [x.strip() for x in cell.split(",") if x.strip()]


def _classify_task(story_id: str, story_index: dict[str, Story]) -> str:
    """Classify a task as F, NF, or SHADOW based on its story link."""
    sid = story_id.strip()
    if not sid or sid == "—":
        return "SHADOW"
    # Linked to a story that exists → Functional
    if sid in story_index:
        return "F"
    # Linked to an epic ID (E-*) but no story → Non-Functional
    if sid.startswith("E-"):
        return "NF"
    # Fallback: if it looks like a story ref but isn't found, still F
    if sid.startswith("S-"):
        return "F"
    return "SHADOW"


def _is_new_bo_format(text: str) -> bool:
    """Detect new BO format: has '## Phase' header AND a table with Weight column."""
    has_phase = bool(re.search(r"^## Phase\s", text, re.MULTILINE))
    has_weight_col = bool(re.search(r"\|\s*Weight\s*\|", text))
    return has_phase and has_weight_col


def _parse_bo_file(text: str) -> list[BO]:
    """Parse new-format BO file into BO objects with nested TBOs.

    Expects:
      ## Phase N: Name   (phase header)
      | ID | Objective | Weight | Status |  (BO table)
      ### BO-N: title    (BO section with TBO subtable)
    """
    if not text.strip():
        return []

    lines = text.splitlines()
    bos: list[BO] = []

    # 1. Find phase header
    phase_name = ""
    for line in lines:
        m = re.match(r"^## (Phase\s+.+)", line.strip())
        if m:
            phase_name = m.group(1).strip()
            break

    # 2. Parse BO table (first table after phase header)
    # Find the phase header index
    phase_idx = 0
    for i, line in enumerate(lines):
        if re.match(r"^## Phase\s", line.strip()):
            phase_idx = i
            break

    # Extract BO table from the text after the phase header
    after_phase = "\n".join(lines[phase_idx:])
    bo_rows = parse_table(after_phase)

    # 3. For each BO row, find its ### section and parse TBO subtable
    bo_sections: dict[str, str] = {}
    section_pattern = re.compile(r"^###\s+(BO-\d+):", re.MULTILINE)
    matches = list(section_pattern.finditer(text))
    for idx, match in enumerate(matches):
        bo_id = match.group(1)
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        bo_sections[bo_id] = text[start:end]

    # 4. Build BO objects
    for row in bo_rows:
        bo_id = row.get("ID", "").strip()
        if not bo_id:
            continue
        weight_str = row.get("Weight", "0").strip()
        try:
            weight = int(weight_str)
        except ValueError:
            weight = 0

        bo = BO(
            id=bo_id,
            objective=row.get("Objective", "").strip(),
            weight=weight,
            status=row.get("Status", "").strip(),
            phase=phase_name,
        )

        # Parse TBO subtable from this BO's section
        section_text = bo_sections.get(bo_id, "")
        if section_text:
            tbo_rows = parse_table(section_text)
            for trow in tbo_rows:
                tbo_id = trow.get("TBO", "").strip()
                if not tbo_id:
                    continue
                tw_str = trow.get("Weight", "0").strip()
                try:
                    tw = int(tw_str)
                except ValueError:
                    tw = 0
                tbo = TBO(
                    id=tbo_id,
                    objective=trow.get("Description", "").strip(),
                    status=trow.get("Status", "").strip(),
                    weight=tw,
                    dod=trow.get("DoD", "").strip(),
                )
                bo.tbos.append(tbo)

        bos.append(bo)

    return bos


def _wrap_flat_tbos_in_bo(tbos: list[TBO]) -> BO:
    """Wrap flat TBO list in a default BO for backward compat."""
    n = len(tbos)
    if n > 0:
        base_weight = 100 // n
        for i, tbo in enumerate(tbos):
            if i == n - 1:
                tbo.weight = 100 - base_weight * (n - 1)
            else:
                tbo.weight = base_weight
    return BO(
        id="BO-1",
        objective="Phase 1 (auto-generated)",
        weight=100,
        status="DRAFT",
        phase="Phase 1",
        tbos=list(tbos),
    )


def load_workbook(docs_dir: Path) -> Workbook:
    """Build the full TBO→Story→Task hierarchy from devlead_docs."""

    # ── Parse raw tables ──
    bo_text = _read_if_exists(docs_dir / "_living_business_objectives.md")
    story_rows = parse_table(_read_if_exists(docs_dir / "_project_stories.md"))
    task_rows = parse_table(_read_if_exists(docs_dir / "_project_tasks.md"))

    # ── Detect BO format ──
    parsed_bos: list[BO] = []
    if bo_text.strip() and _is_new_bo_format(bo_text):
        parsed_bos = _parse_bo_file(bo_text)
        tbo_rows = []  # TBOs come from BO sections, not flat table
    else:
        tbo_rows = parse_table(bo_text)

    # ── Build Story objects ──
    story_index: dict[str, Story] = {}
    for row in story_rows:
        sid = row.get("ID", "").strip()
        if not sid:
            continue
        story = Story(
            id=sid,
            description=row.get("Story", ""),
            epic_id=row.get("Epic", ""),
            tbo_ids=_parse_linked_ids(row.get("TBO Link", "")),
            status=row.get("Status", ""),
            dod=row.get("DoD", ""),
        )
        story_index[sid] = story

    # ── Build Task objects and attach to stories ──
    shadow_tasks: list[Task] = []
    for row in task_rows:
        tid = row.get("ID", "").strip()
        if not tid:
            continue
        story_ref = row.get("Story", "").strip()
        task = Task(
            id=tid,
            description=row.get("Task", ""),
            story_id=story_ref,
            priority=row.get("Priority", ""),
            status=row.get("Status", ""),
            task_type=_classify_task(story_ref, story_index),
            assignee=row.get("Assignee", ""),
        )
        if task.task_type == "SHADOW" or task.task_type == "NF":
            shadow_tasks.append(task)
        elif story_ref in story_index:
            story_index[story_ref].tasks.append(task)
        else:
            # Story ref looks like S-* but not found — still attach as shadow
            shadow_tasks.append(task)

    # ── Build TBO objects and attach stories ──
    tbo_index: dict[str, TBO] = {}
    for row in tbo_rows:
        tbo_id = row.get("ID", "").strip()
        if not tbo_id:
            continue
        tbo = TBO(
            id=tbo_id,
            objective=row.get("Objective", ""),
            status=row.get("Status", ""),
            planned=row.get("Planned", ""),
            actual=row.get("Actual", ""),
            metric=row.get("Metric", ""),
        )
        tbo_index[tbo_id] = tbo

    # Link stories → TBOs
    for story in story_index.values():
        for tbo_id in story.tbo_ids:
            if tbo_id in tbo_index:
                tbo_index[tbo_id].stories.append(story)

    # ── Populate effort data ──
    try:
        from devlead.effort import get_task_effort, get_story_effort

        # Effort for all tasks (linked + shadow)
        all_tasks: list[Task] = shadow_tasks[:]
        for story in story_index.values():
            all_tasks.extend(story.tasks)
        for task in all_tasks:
            effort = get_task_effort(docs_dir, task.id)
            task.total_tokens = effort["total_tokens"]
            task.session_count = effort["session_count"]
            dur_sec = effort.get("duration_estimate", 0)
            task.duration_min = max(1, dur_sec // 60) if dur_sec > 0 else 0

        # Effort for stories (aggregated from child tasks)
        for story in story_index.values():
            s_effort = get_story_effort(docs_dir, story.id)
            story.total_tokens = s_effort["total_tokens"]
            story.session_count = s_effort["session_count"]
            story.duration_min = sum(t.duration_min for t in story.tasks)
    except Exception:
        pass  # Effort data is optional; default zeros are fine

    flat_tbos = list(tbo_index.values())

    # ── Build BO list ──
    if parsed_bos:
        # New format: BOs already have TBOs attached; build flat list
        # Also attach stories to the BO-level TBOs
        for bo in parsed_bos:
            for tbo in bo.tbos:
                # Copy story links from story_index
                for story in story_index.values():
                    if tbo.id in story.tbo_ids:
                        tbo.stories.append(story)
        all_tbos = [tbo for bo in parsed_bos for tbo in bo.tbos]
        return Workbook(
            bos=parsed_bos,
            tbos=all_tbos,
            shadow_tasks=shadow_tasks,
        )
    elif flat_tbos:
        # Old format: wrap in default BO
        default_bo = _wrap_flat_tbos_in_bo(flat_tbos)
        return Workbook(
            bos=[default_bo],
            tbos=flat_tbos,
            shadow_tasks=shadow_tasks,
        )
    else:
        return Workbook(
            tbos=[],
            shadow_tasks=shadow_tasks,
        )
