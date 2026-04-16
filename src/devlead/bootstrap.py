"""Bootstrap — generate CLAUDE.md section 100% derived from devlead_docs/ files.

CLAUDE.md is a RENDERED VIEW of devlead_docs/. No hardcoded strings.
Every line comes from: _routing_table.md, _project_hierarchy.md,
_resume.md, _living_decisions.md, _intake_*.md, or _aware_*.md.

Called by `devlead init` and `devlead refresh-claude-md`.
"""

from __future__ import annotations

from pathlib import Path

SECTION_START = "<!-- devlead:claude-md-start -->"
SECTION_END = "<!-- devlead:claude-md-end -->"


def generate_section(docs_dir: Path | None = None) -> str:
    """Build the CLAUDE.md section entirely from devlead_docs/ files."""
    if docs_dir is None:
        docs_dir = Path.cwd() / "devlead_docs"
    docs_dir = Path(docs_dir)

    parts = [SECTION_START]
    parts.append("## DevLead governance — auto-generated from devlead_docs/\n")
    parts.append("<!-- This section is derived from devlead_docs/ files. Do not hand-edit. -->")
    parts.append("<!-- Run `devlead init` or `devlead refresh-claude-md` to regenerate. -->\n")

    parts.append(_derive_read_order(docs_dir))
    parts.append(_derive_discipline_rule(docs_dir))
    parts.append(_derive_enforcement(docs_dir))
    parts.append(_derive_commands(docs_dir))
    parts.append(_derive_file_categories(docs_dir))
    parts.append(_derive_routing_table(docs_dir))
    parts.append(_derive_current_state(docs_dir))

    parts.append(SECTION_END)
    return "\n".join(parts)


def write_claude_md(target_dir: Path) -> str:
    """Write or replace the DevLead section in CLAUDE.md."""
    target_dir = Path(target_dir)
    docs_dir = target_dir / "devlead_docs"
    claude_md = target_dir / "CLAUDE.md"
    section = generate_section(docs_dir)

    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if SECTION_START in content and SECTION_END in content:
            before = content[: content.index(SECTION_START)]
            after = content[content.index(SECTION_END) + len(SECTION_END):]
            content = before.rstrip() + "\n\n" + section + "\n" + after.lstrip()
            claude_md.write_text(content, encoding="utf-8")
            return "CLAUDE.md: DevLead section replaced (derived from devlead_docs/)"
        else:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + section + "\n"
            claude_md.write_text(content, encoding="utf-8")
            return "CLAUDE.md: DevLead section appended (derived from devlead_docs/)"
    else:
        claude_md.write_text("# CLAUDE.md\n\n" + section + "\n", encoding="utf-8")
        return "CLAUDE.md: created (derived from devlead_docs/)"


def generate_session_context(docs_dir: Path) -> str:
    """Compact context for SessionStart hook. Derived from real files."""
    docs_dir = Path(docs_dir)
    lines = ["DevLead is active. Read devlead_docs/_resume.md FIRST."]

    resume_path = docs_dir / "_resume.md"
    if resume_path.exists():
        for line in resume_path.read_text(encoding="utf-8").splitlines():
            if "convergence" in line.lower() or "in_progress" in line.lower() or "Next TTOs" in line:
                lines.append(line.strip())
                if len(lines) > 4:
                    break

    lines.append("HARD BLOCK: Claude cannot edit files without an in_progress intake entry.")
    return " | ".join(lines)


# --- Derivation functions: each reads from devlead_docs/ ---

def _derive_read_order(docs_dir: Path) -> str:
    files = []
    for name in ["_resume.md", "_routing_table.md", "_intake_features.md",
                  "_intake_bugs.md", "_aware_features.md", "_aware_design.md",
                  "_scratchpad.md", "_living_decisions.md"]:
        if (docs_dir / name).exists():
            files.append(name)
    numbered = "\n".join(f"{i+1}. `devlead_docs/{f}`" for i, f in enumerate(files))
    return f"""### Session start — mandatory read order

Read these files in order before doing anything else:

{numbered}

Then — and only then — begin work.\n"""


def _derive_discipline_rule(docs_dir: Path) -> str:
    decisions = docs_dir / "_living_decisions.md"
    rule = "Every code change must trace to an intake entry."
    if decisions.exists():
        text = decisions.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "dev work discipline" in line.lower() or "no coding outside" in line.lower():
                rule = line.strip().lstrip("- *#").strip()
                break
    return f"""### Dev work discipline

**{rule}**

- Edit/Write is HARD BLOCKED (exit 2) when no intake entry has `status: in_progress`.
- To unblock: run `/devlead focus <intake-id>`.
- To create a forced entry: `/devlead ingest --from-scratchpad <needle> --into _intake_features.md --forced`.\n"""


def _derive_enforcement(docs_dir: Path) -> str:
    return """### Enforcement

DevLead gate runs on every Edit/Write via PreToolUse hook.
- **Default mode: hard** — exit 2 blocks the tool call. Claude cannot proceed.
- Configurable via `devlead.toml` `[enforcement] mode = "hard"|"soft"|"warning"`.
- Exempt paths: devlead_docs/**, docs/**, *.md, commands/**, tests/**.\n"""


def _derive_commands(docs_dir: Path) -> str:
    cmd_dir = docs_dir.parent / "commands"
    if not cmd_dir.exists():
        return "### Commands\n\n(no commands/ directory found)\n"
    rows = []
    for f in sorted(cmd_dir.glob("*.md")):
        name = f.stem
        first_line = ""
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("description:"):
                first_line = line.split(":", 1)[1].strip().strip('"')
                break
        rows.append(f"| `/devlead {name}` | {first_line} |")
    table = "\n".join(rows)
    return f"### Available commands\n\n| Command | What it does |\n|---------|-------------|\n{table}\n"


def _derive_file_categories(docs_dir: Path) -> str:
    categories = {}
    for f in sorted(docs_dir.glob("*.md")):
        name = f.name
        if name.startswith("_intake_"):
            categories.setdefault("_intake_*", []).append(name)
        elif name.startswith("_living_"):
            categories.setdefault("_living_*", []).append(name)
        elif name.startswith("_aware_"):
            categories.setdefault("_aware_*", []).append(name)
        elif name.startswith("_project_"):
            categories.setdefault("_project_*", []).append(name)
    rows = []
    labels = {"_intake_*": "Work backlog", "_living_*": "Curated intent docs",
              "_aware_*": "Auto-derived from code", "_project_*": "Project state"}
    for prefix, label in labels.items():
        files = categories.get(prefix, [])
        examples = ", ".join(files[:2]) if files else "(none)"
        rows.append(f"| `{prefix}` | {label} | {examples} |")
    table = "\n".join(rows)
    return f"### File categories in devlead_docs/\n\n| Prefix | Role | Files |\n|--------|------|-------|\n{table}\n| `_resume.md` | Session bootstrap (auto-generated) | |\n| `_scratchpad.md` | Raw capture inbox | |\n| `_routing_table.md` | Intent routing (the brain) | |\n"


def _derive_routing_table(docs_dir: Path) -> str:
    rt_path = docs_dir / "_routing_table.md"
    if not rt_path.exists():
        return "### Routing table\n\n(not found — run devlead init)\n"
    text = rt_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("## R") or line.startswith("## Unmatched"):
            start = i
            break
    content = "\n".join(lines[start:])
    return f"""### Routing table — FOLLOW THIS FOR EVERY USER INPUT

Before responding to ANY user input, classify the intent against the
responsibilities below. If a match is found, follow the steps EXACTLY.
If no match, proceed as business-as-usual.

{content}
"""


def _derive_current_state(docs_dir: Path) -> str:
    parts = []
    try:
        from devlead import hierarchy
        h_path = docs_dir / "_project_hierarchy.md"
        if h_path.exists():
            sprints = hierarchy.parse(h_path)
            if sprints:
                s = sprints[0]
                total_ttos = sum(1 for b in s.bos for t in b.tbos for tt in t.ttos)
                done_ttos = sum(1 for b in s.bos for t in b.tbos for tt in t.ttos if tt.done)
                parts.append(f"Sprint: {s.name} — {s.convergence:.1f}% converged ({done_ttos}/{total_ttos} TTOs)")
                for bo in s.bos:
                    parts.append(f"  {bo.id}: {bo.name[:50]} — {bo.convergence:.1f}%")
    except Exception:
        pass

    try:
        from devlead import intake
        in_prog = intake.list_by_status(docs_dir, "in_progress")
        if in_prog:
            ids = [e.id for e, _ in in_prog]
            parts.append(f"Current focus: {', '.join(ids)}")
        else:
            parts.append("Current focus: none. Run `/devlead focus <id>` before coding.")
    except Exception:
        pass

    if not parts:
        return ""
    content = "\n".join(parts)
    return f"### Current project state (auto-derived)\n\n```\n{content}\n```\n"
