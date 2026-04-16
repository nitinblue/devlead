"""Source-of-truth (SOT) declaration blocks. Implements FEATURES-0005.

Every devlead_docs/ file opens with a structured metadata block that DevLead
reads to understand the file's role, owner, and lifecycle. Hand-editable;
parsed here with stdlib regex (no YAML dep).

Block format (HTML comment wrapping YAML-ish key/value lines):

    <!-- devlead:sot
      purpose: "Session handoff cursor"
      owner: "claude+user"
      canonical_for: ["session_memory"]
      lineage:
        receives_from: ["_scratchpad.md (via triage)"]
        migrates_to: ["_living_decisions.md (on Sprint close)"]
      lifetime: "permanent"
      bloat_cap_lines: 50
      last_audit: "2026-04-15"
    -->

TODO: wire `/devlead sot list|check` subcommand in cli.py (follow-up).
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


SOT_BLOCK_RE = re.compile(
    r"<!--\s*devlead:sot\s*\n(.*?)\n\s*-->",
    re.DOTALL,
)

_KNOWN_KEYS = {
    "purpose", "owner", "canonical_for", "lineage",
    "lifetime", "bloat_cap_lines", "last_audit",
}
_KNOWN_LINEAGE_KEYS = {"receives_from", "migrates_to"}


@dataclass
class SotBlock:
    purpose: str = ""
    owner: str = ""
    canonical_for: list[str] = field(default_factory=list)
    receives_from: list[str] = field(default_factory=list)
    migrates_to: list[str] = field(default_factory=list)
    lifetime: str = "permanent"
    bloat_cap_lines: int | None = None
    last_audit: str | None = None


def parse(file_path: Path) -> SotBlock | None:
    """Read a file and return its SotBlock, or None if no block present."""
    p = Path(file_path)
    if not p.exists():
        return None
    return parse_text(p.read_text(encoding="utf-8"))


def parse_text(text: str) -> SotBlock | None:
    """Parse the first SOT block found in `text`. Returns None if absent."""
    m = SOT_BLOCK_RE.search(text)
    if not m:
        return None

    body = m.group(1)
    block = SotBlock()
    in_lineage = False

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent >= 4 and in_lineage:
            key, _, value = stripped.partition(":")
            key = key.strip()
            if key not in _KNOWN_LINEAGE_KEYS:
                print(f"sot: unknown lineage key {key!r}", file=sys.stderr)
                continue
            values = _parse_list(value.strip())
            if key == "receives_from":
                block.receives_from = values
            else:
                block.migrates_to = values
            continue

        in_lineage = False
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if key == "lineage":
            in_lineage = True
            continue

        if key not in _KNOWN_KEYS:
            print(f"sot: unknown key {key!r}", file=sys.stderr)
            continue

        if key == "purpose":
            block.purpose = _parse_string(value)
        elif key == "owner":
            block.owner = _parse_string(value)
        elif key == "canonical_for":
            block.canonical_for = _parse_list(value)
        elif key == "lifetime":
            block.lifetime = _parse_string(value) or "permanent"
        elif key == "bloat_cap_lines":
            try:
                block.bloat_cap_lines = int(value) if value else None
            except ValueError:
                print(f"sot: bad bloat_cap_lines {value!r}", file=sys.stderr)
        elif key == "last_audit":
            block.last_audit = _parse_string(value) or None

    return block


def render(block: SotBlock) -> str:
    """Render a SotBlock to the HTML-comment string for injection into a file."""
    lines = ["<!-- devlead:sot"]
    lines.append(f'  purpose: {_quote(block.purpose)}')
    lines.append(f'  owner: {_quote(block.owner)}')
    lines.append(f"  canonical_for: {_render_list(block.canonical_for)}")
    lines.append("  lineage:")
    lines.append(f"    receives_from: {_render_list(block.receives_from)}")
    lines.append(f"    migrates_to: {_render_list(block.migrates_to)}")
    lines.append(f'  lifetime: {_quote(block.lifetime)}')
    if block.bloat_cap_lines is not None:
        lines.append(f"  bloat_cap_lines: {block.bloat_cap_lines}")
    if block.last_audit:
        lines.append(f'  last_audit: {_quote(block.last_audit)}')
    lines.append("-->")
    return "\n".join(lines)


def read_all(docs_dir: Path) -> dict[str, SotBlock]:
    """Parse every *.md file in docs_dir. Returns {filename: block} skipping files without a block."""
    out: dict[str, SotBlock] = {}
    for md_path in sorted(Path(docs_dir).glob("*.md")):
        block = parse(md_path)
        if block is not None:
            out[md_path.name] = block
    return out


def _parse_string(value: str) -> str:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def _parse_list(value: str) -> list[str]:
    value = value.strip()
    if not value or value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1]
        parts = [p.strip() for p in inner.split(",") if p.strip()]
        return [_parse_string(p) for p in parts]
    return [_parse_string(value)]


def _quote(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


def _render_list(items: list[str]) -> str:
    if not items:
        return "[]"
    quoted = ", ".join(_quote(i) for i in items)
    return f"[{quoted}]"
