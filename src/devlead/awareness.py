"""Self-awareness layer - generates _aware_*.md files from the codebase.

The awareness module is a pure scanner: it reads `commands/*.md` and
`src/devlead/*.py` and writes structured descriptive snapshots into
`devlead_docs/_aware_features.md` and `devlead_docs/_aware_design.md`.

These files are DERIVED from code and describe CURRENT state (not aspirational
design). They are overwritten every run; hand-edits are lost.

v1 ships two aspects (features, design). v1.1 adds metrics, dependencies,
invariants, and a Stop-hook auto-refresh so the files stay current without
manual intervention.

ASCII only. Stdlib only. No LLM calls.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)
_MODULE_DOCSTRING_RE = re.compile(r'^"""(.+?)"""', re.DOTALL)
_DEF_RE = re.compile(r"^(?:def|class)\s+([A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)
_FROM_DEVLEAD_RE = re.compile(
    r"^\s*from\s+(devlead\.[A-Za-z_][A-Za-z0-9_]*)\s+import\s+", re.MULTILINE
)


@dataclass
class Feature:
    name: str
    kind: str
    description: str
    command_file: str
    handler: str = ""
    trace: str = ""


@dataclass
class Module:
    name: str
    path: str
    purpose: str
    public_api: list[str] = field(default_factory=list)
    line_count: int = 0
    depends_on: list[str] = field(default_factory=list)


@dataclass
class ProjectSnapshot:
    timestamp: str
    features: list[Feature] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)


def scan(repo_root: Path) -> ProjectSnapshot:
    """Produce a ProjectSnapshot by reading the repo's commands/ and src/."""
    repo_root = Path(repo_root)
    snapshot = ProjectSnapshot(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    snapshot.features = _scan_features(repo_root)
    snapshot.modules = _scan_modules(repo_root)
    return snapshot


def _scan_features(repo_root: Path) -> list[Feature]:
    commands_dir = repo_root / "commands"
    if not commands_dir.is_dir():
        return []
    cli_path = repo_root / "src" / "devlead" / "cli.py"
    cli_raw = cli_path.read_text(encoding="utf-8") if cli_path.exists() else ""

    features: list[Feature] = []
    for cmd_file in sorted(commands_dir.glob("*.md")):
        raw = cmd_file.read_text(encoding="utf-8")
        description = ""
        fm_match = _FRONTMATTER_RE.search(raw)
        if fm_match:
            desc_match = _DESC_RE.search(fm_match.group(1))
            if desc_match:
                description = desc_match.group(1).strip().strip('"').strip("'")

        name = cmd_file.stem
        handler_func = f"_cmd_{name}"
        handler_ref = (
            f"src/devlead/cli.py:{handler_func}" if handler_func in cli_raw else ""
        )

        features.append(Feature(
            name=name,
            kind="slash-command",
            description=description,
            command_file=str(cmd_file.relative_to(repo_root)).replace("\\", "/"),
            handler=handler_ref,
        ))
    return features


def _scan_modules(repo_root: Path) -> list[Module]:
    src_dir = repo_root / "src" / "devlead"
    if not src_dir.is_dir():
        return []
    modules: list[Module] = []
    for py_file in sorted(src_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        raw = py_file.read_text(encoding="utf-8")

        purpose = ""
        docstring_match = _MODULE_DOCSTRING_RE.match(raw)
        if docstring_match:
            first_line = docstring_match.group(1).strip().splitlines()[0]
            purpose = first_line.strip()

        public: list[str] = []
        for m in _DEF_RE.finditer(raw):
            n = m.group(1)
            if not n.startswith("_") and n not in public:
                public.append(n)

        depends: list[str] = []
        for m in _FROM_DEVLEAD_RE.finditer(raw):
            dep = m.group(1)
            if dep != f"devlead.{py_file.stem}" and dep not in depends:
                depends.append(dep)

        modules.append(Module(
            name=f"devlead.{py_file.stem}",
            path=str(py_file.relative_to(repo_root)).replace("\\", "/"),
            purpose=purpose,
            public_api=public,
            line_count=len(raw.splitlines()),
            depends_on=sorted(depends),
        ))
    return modules


def render_features(snapshot: ProjectSnapshot, output_path: Path) -> None:
    lines = [
        "# _aware_features.md",
        "",
        "> **Self-awareness file.** Auto-generated inventory of every feature",
        "> this project exposes. DO NOT EDIT - run `/devlead awareness` to refresh.",
        "> Hand-edits are overwritten on next refresh.",
        ">",
        f"> **Last refresh:** {snapshot.timestamp}",
        "> **Generator:** devlead.awareness v1",
        "> **Scan sources:** commands/*.md, src/devlead/cli.py",
        "",
        "---",
        "",
        "## Slash commands",
        "",
    ]
    if not snapshot.features:
        lines.append("*(No slash commands found.)*")
    else:
        for f in snapshot.features:
            lines.append(f"### /devlead {f.name}")
            lines.append(f"- **Kind:** {f.kind}")
            lines.append(f"- **Description:** {f.description or '(none)'}")
            lines.append(f"- **Command file:** `{f.command_file}`")
            if f.handler:
                lines.append(f"- **Handler:** `{f.handler}`")
            if f.trace:
                lines.append(f"- **Trace:** {f.trace}")
            lines.append("")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_design(snapshot: ProjectSnapshot, output_path: Path) -> None:
    lines = [
        "# _aware_design.md",
        "",
        "> **Self-awareness file.** Auto-generated snapshot of the project's",
        "> current technical design. DO NOT EDIT - run `/devlead awareness` to",
        "> refresh. Hand-edits are overwritten on next refresh.",
        ">",
        f"> **Last refresh:** {snapshot.timestamp}",
        "> **Generator:** devlead.awareness v1",
        "> **Scan source:** src/devlead/*.py (module docstrings + public API + deps)",
        "",
        "---",
        "",
        "## Modules",
        "",
    ]
    if not snapshot.modules:
        lines.append("*(No modules found.)*")
    else:
        for m in snapshot.modules:
            lines.append(f"### `{m.name}`")
            lines.append(f"- **Path:** `{m.path}`")
            lines.append(f"- **Purpose:** {m.purpose or '(no docstring)'}")
            lines.append(f"- **Lines:** {m.line_count}")
            if m.public_api:
                lines.append(f"- **Public API:** `{', '.join(m.public_api)}`")
            else:
                lines.append("- **Public API:** (none)")
            if m.depends_on:
                lines.append(
                    "- **Depends on:** " + ", ".join(f"`{d}`" for d in m.depends_on)
                )
            else:
                lines.append("- **Depends on:** (stdlib only)")
            lines.append("")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def refresh(repo_root: Path, docs_dir: Path) -> tuple[Path, Path]:
    """Scan the repo and rewrite both _aware_*.md files. Returns their paths."""
    snapshot = scan(repo_root)
    features_path = Path(docs_dir) / "_aware_features.md"
    design_path = Path(docs_dir) / "_aware_design.md"
    render_features(snapshot, features_path)
    render_design(snapshot, design_path)
    return features_path, design_path


def _main(argv: list[str]) -> int:
    repo_root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    docs_dir = repo_root / "devlead_docs"
    if not docs_dir.exists():
        print(f"error: {docs_dir} not found; run `devlead init` first")
        return 1
    features_path, design_path = refresh(repo_root, docs_dir)
    print(f"refreshed: {features_path.relative_to(repo_root)}")
    print(f"refreshed: {design_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
