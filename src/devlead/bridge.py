"""Plugin bridge - ingest a plugin plan OR a scratchpad entry into an intake file.

Claude-driven v1. Two ingest paths:

  1. `ingest(plan_path, into, docs_dir)` - for plugin-produced plans/specs
     (e.g. superpowers writing-plans output). Reads a markdown file, extracts
     title/summary/actions, writes an intake entry.

  2. `ingest_from_scratchpad(scratchpad_path, needle, into, docs_dir)` -
     converts an existing scratchpad entry directly into an intake entry.
     Used by the triage -> intake path. Annotates the scratchpad entry with
     a cross-reference line pointing at the new intake ID.

Every intake entry records its source (plan path or `scratchpad:<entry-id>`)
so the full trace from raw note -> intake -> TTO -> commit remains intact.

No plugin is modified, wrapped, hooked, or imported. Ingest runs AFTER a
plugin finishes, on a file the plugin has already written.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from devlead import audit, intake


_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
_CHECKBOX_RE = re.compile(r"^\s*-\s+\[[ xX]\]\s+(.+?)\s*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$")

_ASCII_MAP = {
    "\u2014": "-",    # em dash
    "\u2013": "-",    # en dash
    "\u2192": "->",   # right arrow
    "\u2190": "<-",   # left arrow
    "\u2018": "'",    # left single quote
    "\u2019": "'",    # right single quote
    "\u201c": '"',    # left double quote
    "\u201d": '"',    # right double quote
    "\u2026": "...",  # ellipsis
    "\u00a0": " ",    # non-breaking space
    "\u2022": "*",    # bullet
}


def ingest(
    plugin_plan_path: Path,
    into_file: str | Path,
    devlead_docs_dir: Path,
    *,
    proposed_bo: str = "(needs BO)",
    proposed_sprint: str = "(needs sprint)",
    proposed_weight: str = "(needs weight)",
    origin: str = "normal",
) -> intake.IntakeEntry:
    """Parse a plugin plan file and append an entry to the given intake file.

    `into_file` can be a bare filename (resolved relative to devlead_docs_dir)
    or an absolute path. It must match `_intake_*.md`.

    `origin` marks how the entry was created. Values in use:
      - "normal" - flowed through scratchpad -> triage -> plugin plan -> ingest
      - "forced" - user dictated work outside the normal flow; Claude created
                   this entry post-hoc as the discipline rule requires a trace
    """
    plugin_plan_path = Path(plugin_plan_path)
    if not plugin_plan_path.exists():
        raise FileNotFoundError(f"plugin plan not found: {plugin_plan_path}")

    into_path = _resolve_into(into_file, devlead_docs_dir)
    _warn_if_no_template(into_path, devlead_docs_dir)

    raw = plugin_plan_path.read_text(encoding="utf-8")
    entry = intake.IntakeEntry(
        id=intake.next_id(into_path),
        title=_extract_title(raw, fallback=plugin_plan_path.stem),
        source=str(plugin_plan_path).replace("\\", "/"),
        captured=_utc_now(),
        summary=_extract_summary(raw),
        actionable_items=_extract_actions(raw),
        proposed_bo=proposed_bo,
        proposed_sprint=proposed_sprint,
        proposed_weight=proposed_weight,
        origin=origin,
    )
    intake.add_entry(into_path, entry)
    _warn_if_no_actions(entry)
    audit.append_event(
        Path(devlead_docs_dir), "ingest", intake_id=entry.id,
        source=entry.source, origin=entry.origin, result="ok",
    )
    return entry


def ingest_from_scratchpad(
    scratchpad_path: Path,
    entry_needle: str,
    into_file: str | Path,
    devlead_docs_dir: Path,
    *,
    proposed_bo: str = "(needs BO)",
    proposed_sprint: str = "(needs sprint)",
    proposed_weight: str = "(needs weight)",
    origin: str = "normal",
) -> intake.IntakeEntry:
    """Convert a scratchpad entry directly into an intake entry.

    Looks up the scratchpad entry by substring match on id or title, extracts
    summary/actions from its body, writes an intake entry, and annotates the
    scratchpad entry with a cross-reference line.

    The entry's source is recorded as `scratchpad:<entry-id>` so traceability
    back to the original raw capture is preserved.
    """
    from devlead import scratchpad as scratchpad_mod

    scratchpad_path = Path(scratchpad_path)
    if not scratchpad_path.exists():
        raise FileNotFoundError(f"scratchpad not found: {scratchpad_path}")

    match = scratchpad_mod.get_entry(scratchpad_path, entry_needle)
    if match is None:
        raise ValueError(f"no scratchpad entry matching: {entry_needle!r}")
    entry_id, title, body = match

    into_path = _resolve_into(into_file, devlead_docs_dir)
    _warn_if_no_template(into_path, devlead_docs_dir)

    synthetic_raw = f"# {title}\n\n{body}\n"
    entry = intake.IntakeEntry(
        id=intake.next_id(into_path),
        title=_to_ascii(title)[:120],
        source=f"scratchpad:{entry_id}",
        captured=_utc_now(),
        summary=_extract_summary(synthetic_raw),
        actionable_items=_extract_actions(synthetic_raw),
        proposed_bo=proposed_bo,
        proposed_sprint=proposed_sprint,
        proposed_weight=proposed_weight,
        origin=origin,
        derived_from=[entry_id],
    )
    intake.add_entry(into_path, entry)
    _warn_if_no_actions(entry)

    note = f"> **Promoted:** tracked as `{entry.id}` in `{into_path.name}`."
    scratchpad_mod.append_cross_reference(scratchpad_path, entry_id, note)
    audit.append_event(
        Path(devlead_docs_dir), "ingest_from_scratchpad", intake_id=entry.id,
        source=entry.source, origin=entry.origin, result="ok",
    )
    return entry


def promote_to_living(
    scratchpad_path: Path,
    entry_needle: str,
    into_file: str | Path,
    devlead_docs_dir: Path,
) -> str:
    """Migrate a scratchpad entry's body into a `_living_*.md` file.

    Appends a new section to the target living file, cross-references the
    scratchpad entry, and returns a one-line summary of the migration.
    """
    from devlead import scratchpad as scratchpad_mod

    scratchpad_path = Path(scratchpad_path)
    if not scratchpad_path.exists():
        raise FileNotFoundError(f"scratchpad not found: {scratchpad_path}")

    match = scratchpad_mod.get_entry(scratchpad_path, entry_needle)
    if match is None:
        raise ValueError(f"no scratchpad entry matching: {entry_needle!r}")
    entry_id, title, body = match

    into_path = Path(into_file)
    if not into_path.is_absolute():
        into_path = Path(devlead_docs_dir) / into_path
    if not into_path.name.startswith("_living_") or not into_path.name.endswith(".md"):
        raise ValueError(
            f"into file must match _living_*.md pattern: {into_path.name}"
        )
    if not into_path.exists():
        raise FileNotFoundError(f"living file not found: {into_path}")

    section = (
        f"\n## {_to_ascii(title)}\n\n"
        f"_From scratchpad {entry_id}, migrated {_utc_now()}_\n\n"
        f"{_to_ascii(body)}\n\n---\n"
    )
    existing = into_path.read_text(encoding="utf-8")
    if not existing.endswith("\n"):
        existing += "\n"
    into_path.write_text(existing + section, encoding="utf-8")

    note = f"> **Migrated:** content moved to `{into_path.name}` on {_utc_now()}."
    scratchpad_mod.append_cross_reference(scratchpad_path, entry_id, note)

    audit.append_event(
        Path(devlead_docs_dir), "promote_to_living",
        source=f"scratchpad:{entry_id}", file=into_path.name, result="ok",
    )
    return f"{into_path.name} <- {title}"


def _resolve_into(into_file: str | Path, devlead_docs_dir: Path) -> Path:
    into_path = Path(into_file)
    if not into_path.is_absolute():
        into_path = Path(devlead_docs_dir) / into_path
    if not into_path.name.startswith("_intake_") or not into_path.name.endswith(".md"):
        raise ValueError(
            f"into file must match _intake_*.md pattern: {into_path.name}"
        )
    return into_path


def _warn_if_no_template(into_path: Path, devlead_docs_dir: Path) -> None:
    if intake.template_path_for(into_path, Path(devlead_docs_dir)) is None:
        print(
            f"warning: no template found for {into_path.name} "
            f"(expected at {devlead_docs_dir}/_intake_templates/)",
            file=sys.stderr,
        )


def _warn_if_no_actions(entry: intake.IntakeEntry) -> None:
    if not entry.actionable_items:
        print(
            f"warning: {entry.id} has no actionable items; "
            f"every TBO must map to granular TTOs - refine or reject before promoting",
            file=sys.stderr,
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_ascii(text: str) -> str:
    for u, a in _ASCII_MAP.items():
        text = text.replace(u, a)
    return "".join(c if ord(c) <= 126 else "?" for c in text)


def _extract_title(raw: str, fallback: str) -> str:
    m = _H1_RE.search(raw)
    if not m:
        return _to_ascii(fallback)
    title = _to_ascii(m.group(1).strip())
    title = re.sub(r"^(Plan|Spec|Design)\s*[-:]\s*", "", title, flags=re.IGNORECASE)
    return title[:120]


def _extract_summary(raw: str) -> str:
    body = raw
    ctx = re.search(r"^##\s+Context\s*$", raw, flags=re.MULTILINE)
    if ctx:
        body = raw[ctx.end():]
    else:
        h1 = _H1_RE.search(raw)
        if h1:
            body = raw[h1.end():]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    for p in paragraphs:
        if p.lstrip().startswith("#"):
            continue
        flat = " ".join(p.split())
        return _to_ascii(flat[:240])
    return ""


def _extract_actions(raw: str) -> list[str]:
    checkboxes = [m.group(1).strip() for m in _CHECKBOX_RE.finditer(raw)]
    if checkboxes:
        return [_clean_item(x) for x in checkboxes[:20]]

    section_titles = {"scope", "files to create", "files to modify", "tasks", "steps"}
    out: list[str] = []
    current_section: str | None = None
    for line in raw.splitlines():
        hm = _H2_RE.match(line)
        if hm:
            current_section = hm.group(1).strip().lower()
            continue
        if current_section in section_titles:
            bm = _BULLET_RE.match(line)
            if bm:
                out.append(_clean_item(bm.group(1).strip()))
    return out[:20]


def _clean_item(item: str) -> str:
    item = re.sub(r"\*\*(.*?)\*\*", r"\1", item)
    item = re.sub(r"`([^`]+)`", r"\1", item)
    return _to_ascii(item.strip())
