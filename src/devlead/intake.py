"""Intake file layer - read/write any `_intake_*.md` file.

Intake files are pure markdown. Each entry is a level-2 heading of the form:

    ## FEATURES-0001 - Title
    - **Source:** path/or/reference
    - **Captured:** 2026-04-14T14:32:00Z
    - **Summary:** one-line distillation
    - **Actionable items:**
      - [ ] item one
      - [ ] item two
    - **Proposed BO:** (needs BO)
    - **Proposed Sprint:** (needs sprint)
    - **Proposed weight:** (needs weight)
    - **Status:** pending
    - **Promoted to:** (pending)
    - **Promoted at:** (pending)

ID prefix is derived from the filename slug: `_intake_features.md` -> `FEATURES`,
`_intake_security_findings.md` -> `SECURITY-FINDINGS`. No hardcoded constants.

Each intake file has a matching template under `devlead_docs/_intake_templates/`
that documents the allowed fields. The template is editable; v1 does not parse
it for schema enforcement (hardcoded in this module), but v1.1 will.

ASCII only. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re


_HEADING_RE = re.compile(r"^##\s+([A-Z][A-Z0-9-]*-\d{4})\s+-\s+(.+?)\s*$")
_FIELD_RE = re.compile(r"^-\s+\*\*(?P<key>[^:*]+):\*\*\s*(?P<value>.*?)\s*$")
_ACTION_RE = re.compile(r"^\s+-\s+\[[ xX]\]\s+(.+?)\s*$")
_ID_NUM_RE = re.compile(r"^([A-Z][A-Z0-9-]*)-(\d{4})$")


@dataclass
class IntakeEntry:
    id: str
    title: str
    source: str
    captured: str
    summary: str = ""
    actionable_items: list[str] = field(default_factory=list)
    proposed_bo: str = "(needs BO)"
    proposed_sprint: str = "(needs sprint)"
    proposed_weight: str = "(needs weight)"
    status: str = "pending"
    origin: str = "normal"
    promoted_to: str = "(pending)"
    promoted_at: str = "(pending)"
    derived_from: list[str] = field(default_factory=list)
    descendants: list[str] = field(default_factory=list)
    supersedes: str | None = None

    def to_markdown(self) -> str:
        lines = [
            f"## {self.id} - {self.title}",
            f"- **Source:** {self.source}",
            f"- **Captured:** {self.captured}",
            f"- **Summary:** {self.summary}",
            "- **Actionable items:**",
        ]
        if self.actionable_items:
            for item in self.actionable_items:
                lines.append(f"  - [ ] {item}")
        else:
            lines.append("  - (none)")
        lines.extend([
            f"- **Proposed BO:** {self.proposed_bo}",
            f"- **Proposed Sprint:** {self.proposed_sprint}",
            f"- **Proposed weight:** {self.proposed_weight}",
            f"- **Status:** {self.status}",
            f"- **Origin:** {self.origin}",
            f"- **Promoted to:** {self.promoted_to}",
            f"- **Promoted at:** {self.promoted_at}",
            f"- **Derived from:** {', '.join(self.derived_from) if self.derived_from else '(none)'}",
            f"- **Descendants:** {', '.join(self.descendants) if self.descendants else '(none)'}",
            f"- **Supersedes:** {self.supersedes if self.supersedes else '(none)'}",
        ])
        return "\n".join(lines) + "\n"


def prefix_from_path(intake_path: Path) -> str:
    """Derive the ID prefix from an intake filename.

    _intake_features.md -> 'FEATURES'
    _intake_bugs.md -> 'BUGS'
    _intake_security_findings.md -> 'SECURITY-FINDINGS'
    """
    stem = Path(intake_path).stem
    if not stem.startswith("_intake_"):
        raise ValueError(f"not an intake file (must start with _intake_): {intake_path}")
    slug = stem[len("_intake_"):]
    if not slug:
        raise ValueError(f"empty intake slug: {intake_path}")
    return slug.upper().replace("_", "-")


def template_path_for(intake_path: Path, docs_dir: Path) -> Path | None:
    """Return the template file used by any intake file, or None if missing.

    v1 ships ONE template at `<docs_dir>/_intake_templates/default.md`.
    All intake files use it. v1.1+ will add a picker so users can declare
    which template an intake file uses (via a header line or a --template
    flag on ingest).
    """
    if not Path(intake_path).stem.startswith("_intake_"):
        return None
    default_path = Path(docs_dir) / "_intake_templates" / "default.md"
    if default_path.exists():
        return default_path
    return None


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def read(intake_path: Path) -> list[IntakeEntry]:
    """Parse all ## entries in an intake file into IntakeEntry objects."""
    if not intake_path.exists():
        return []
    raw = _strip_html_comments(intake_path.read_text(encoding="utf-8"))
    lines = raw.splitlines()
    entries: list[IntakeEntry] = []
    current: IntakeEntry | None = None
    in_actions = False
    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            if current is not None:
                entries.append(current)
            current = IntakeEntry(id=m.group(1), title=m.group(2), source="", captured="")
            in_actions = False
            continue
        if current is None:
            continue
        fm = _FIELD_RE.match(line)
        if fm:
            key = fm.group("key").strip().lower()
            value = fm.group("value").strip()
            if key == "source":
                current.source = value
            elif key == "captured":
                current.captured = value
            elif key == "summary":
                current.summary = value
            elif key == "actionable items":
                in_actions = True
                continue
            elif key == "proposed bo":
                current.proposed_bo = value or "(needs BO)"
                in_actions = False
            elif key == "proposed sprint":
                current.proposed_sprint = value or "(needs sprint)"
                in_actions = False
            elif key == "proposed weight":
                current.proposed_weight = value or "(needs weight)"
                in_actions = False
            elif key == "status":
                current.status = value or "pending"
                in_actions = False
            elif key == "origin":
                current.origin = value or "normal"
                in_actions = False
            elif key == "promoted to":
                current.promoted_to = value or "(pending)"
                in_actions = False
            elif key == "promoted at":
                current.promoted_at = value or "(pending)"
                in_actions = False
            elif key == "derived from":
                if value and value.strip() != "(none)":
                    current.derived_from = [v.strip() for v in value.split(",") if v.strip()]
                in_actions = False
            elif key == "descendants":
                if value and value.strip() != "(none)":
                    current.descendants = [v.strip() for v in value.split(",") if v.strip()]
                in_actions = False
            elif key == "supersedes":
                if value and value.strip() != "(none)":
                    current.supersedes = value.strip()
                in_actions = False
            continue
        if in_actions:
            am = _ACTION_RE.match(line)
            if am:
                item = am.group(1).strip()
                if item.lower() != "(none)":
                    current.actionable_items.append(item)
    if current is not None:
        entries.append(current)
    return entries


def next_id(intake_path: Path) -> str:
    """Return the next available ID for this intake file, derived from its filename."""
    prefix = prefix_from_path(intake_path)
    max_n = 0
    if intake_path.exists():
        raw = _strip_html_comments(intake_path.read_text(encoding="utf-8"))
        for line in raw.splitlines():
            m = _HEADING_RE.match(line)
            if not m:
                continue
            idm = _ID_NUM_RE.match(m.group(1))
            if idm and idm.group(1) == prefix:
                n = int(idm.group(2))
                if n > max_n:
                    max_n = n
    return f"{prefix}-{max_n + 1:04d}"


def add_entry(intake_path: Path, entry: IntakeEntry) -> None:
    """Append entry.to_markdown() to the intake file, preserving existing content."""
    block = entry.to_markdown()
    if not intake_path.exists():
        intake_path.write_text(block, encoding="utf-8")
        return
    existing = intake_path.read_text(encoding="utf-8")
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing and not existing.endswith("\n\n"):
        existing += "\n"
    intake_path.write_text(existing + block, encoding="utf-8")


def find_entry(docs_dir: Path, entity_id: str) -> tuple[IntakeEntry, Path] | None:
    """Find an intake entry by ID across all _intake_*.md files in docs_dir."""
    docs_dir = Path(docs_dir)
    for f in sorted(docs_dir.glob("_intake_*.md")):
        for entry in read(f):
            if entry.id == entity_id:
                return entry, f
    return None


def list_by_status(
    docs_dir: Path, status: str
) -> list[tuple[IntakeEntry, Path]]:
    """Return all entries matching the given status across all intake files."""
    docs_dir = Path(docs_dir)
    results: list[tuple[IntakeEntry, Path]] = []
    for f in sorted(docs_dir.glob("_intake_*.md")):
        for entry in read(f):
            if entry.status == status:
                results.append((entry, f))
    return results


def update_status(intake_path: Path, entity_id: str, new_status: str) -> bool:
    """Flip the Status field of one intake entry in place. Returns True if updated."""
    path = Path(intake_path)
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    in_target = False
    updated = False
    heading_prefix = f"## {entity_id} -"
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            in_target = True
            continue
        if in_target and line.startswith("## "):
            in_target = False
        if in_target and line.startswith("- **Status:**"):
            lines[i] = f"- **Status:** {new_status}"
            updated = True
            in_target = False
    if updated:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return updated


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: python -m devlead.intake <path-to-intake-file>")
        return 2
    path = Path(argv[1])
    entries = read(path)
    if not entries:
        print("(no entries)")
        return 0
    for e in entries:
        print(f"{e.id}  {e.status:<9}  {e.title}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
