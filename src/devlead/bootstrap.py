"""Bootstrap — generate the CLAUDE.md section that teaches the LLM how DevLead works.

Called by `devlead init` to append a comprehensive governance section to the
target project's CLAUDE.md. This is the PRIMARY mechanism by which a fresh
Claude session learns about DevLead — without it, all the infrastructure
(intake files, SOT blocks, gates, audit logs) is invisible to the model.

The generated section is self-contained and auto-derived from the current
DevLead feature set. Re-running `devlead init` on an existing project
regenerates it (idempotent: replaces the old section if present).
"""

from __future__ import annotations

from pathlib import Path

SECTION_START = "<!-- devlead:claude-md-start -->"
SECTION_END = "<!-- devlead:claude-md-end -->"


def generate_section() -> str:
    """Return the full CLAUDE.md section text for DevLead governance."""
    return f"""{SECTION_START}
## DevLead governance — read every session

This project uses **DevLead**, a governance tool that is the single channel
between you (the LLM) and the codebase. Every task traces through DevLead's
document store. These rules are non-negotiable.

### Session start — mandatory read order

At the start of **every** session, before doing anything else, read these files
in this exact order:

1. `devlead_docs/_resume.md` — thin bootstrap cursor (~30-50 lines): current
   focus, read order, next action, open blockers.
2. `devlead_docs/_intake_*.md` — scan for entries with `status: in_progress`.
   Those are the current focus. Run `/devlead focus show` to list them.
3. `devlead_docs/_aware_features.md` and `_aware_design.md` — auto-derived
   snapshots of what the code actually does right now.
4. `devlead_docs/_scratchpad.md` — raw untriaged capture from prior sessions.
5. `devlead_docs/_living_decisions.md` — canonical locked-decisions archive.

Then — and only then — begin work.

### Dev work discipline — no code without intake trace

**Hard rule:** every code change (edit, new file, bug fix, refactor) must
originate from an entry in `devlead_docs/_intake_*.md`. No exceptions.

- **New feature:** capture to `_scratchpad.md` → triage → ingest into
  `_intake_features.md` → implement.
- **Bug noticed mid-task:** STOP. Append to `_scratchpad.md`. Run
  `/devlead ingest --from-scratchpad <needle> --into _intake_bugs.md`.
  Only then fix it.
- **User forces work without pre-existing intake:** create the intake entry
  FIRST with `--forced` flag, THEN do the work. Never refuse, never skip.

### Enforcement gate

The discipline rule is backed by `/devlead gate`. When a `PreToolUse` hook
fires without an `in_progress` intake entry, the gate writes a `gate_warn`
audit event and injects a systemMessage nudge. Warn-only — never blocks.

### Available commands

| Command | What it does |
|---------|-------------|
| `/devlead init` | Install DevLead on a project |
| `/devlead scratchpad` | List raw capture entries |
| `/devlead scratchpad archive` | Archive promoted entries |
| `/devlead intake` | List all intake file entries |
| `/devlead triage` | Walk scratchpad for routing |
| `/devlead ingest <plan> --into <file>` | Ingest a plugin plan into intake |
| `/devlead promote <needle> --to intake\\|decision\\|fact` | Route scratchpad entries |
| `/devlead focus [show\\|clear\\|<id>]` | Set/show/clear current work focus |
| `/devlead awareness` | Refresh `_aware_*.md` from code |
| `/devlead gate <HookName>` | Run enforcement gate (stdin JSON) |
| `/devlead migrate <src> <heading> --to <dest>` | Hash-checked content migration |
| `/devlead verify-links` | Check cross-references for broken refs |
| `/devlead audit recent [N]` | Print recent audit events |
| `/devlead config show` | Show resolved config |

### File categories in devlead_docs/

| Prefix | Role | Examples |
|--------|------|---------|
| `_intake_*` | Work backlog (features, bugs) | `_intake_features.md` |
| `_living_*` | Curated intent docs (decisions, goals) | `_living_decisions.md` |
| `_aware_*` | Auto-derived from code (regenerated) | `_aware_features.md` |
| `_project_*` | Project state (hierarchy, status) | `_project_hierarchy.md` |
| `_resume.md` | Session bootstrap cursor | |
| `_scratchpad.md` | Raw untriaged capture inbox | |

### SOT blocks

Every file in `devlead_docs/` opens with a `<!-- devlead:sot ... -->` metadata
block declaring its purpose, owner, lineage, and lifetime. DevLead reads these
to understand the file's role. Do not remove them.
{SECTION_END}"""


def write_claude_md(target_dir: Path) -> str:
    """Append (or replace) the DevLead section in CLAUDE.md. Returns status message."""
    claude_md = Path(target_dir) / "CLAUDE.md"
    section = generate_section()

    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8")
        if SECTION_START in content and SECTION_END in content:
            before = content[: content.index(SECTION_START)]
            after = content[content.index(SECTION_END) + len(SECTION_END) :]
            content = before.rstrip() + "\n\n" + section + "\n" + after.lstrip()
            claude_md.write_text(content, encoding="utf-8")
            return "CLAUDE.md: DevLead section replaced (updated)"
        else:
            if not content.endswith("\n"):
                content += "\n"
            content += "\n" + section + "\n"
            claude_md.write_text(content, encoding="utf-8")
            return "CLAUDE.md: DevLead section appended"
    else:
        claude_md.write_text("# CLAUDE.md\n\n" + section + "\n", encoding="utf-8")
        return "CLAUDE.md: created with DevLead section"


def generate_session_context(docs_dir: Path) -> str:
    """Generate a compact session-start context string for the SessionStart hook."""
    lines = ["DevLead is active on this project. Read devlead_docs/_resume.md FIRST."]

    resume_path = docs_dir / "_resume.md"
    if resume_path.exists():
        text = resume_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("**Currently in_progress:**"):
                lines.append(line)
                break

    try:
        from devlead import intake
        in_progress = intake.list_by_status(docs_dir, "in_progress")
        if in_progress:
            ids = [e.id for e, _ in in_progress]
            lines.append(f"Focus: {', '.join(ids)}")
        else:
            lines.append("Focus: none set. Run `/devlead focus <intake-id>` before editing code.")

        pending_count = 0
        for f in sorted(docs_dir.glob("_intake_*.md")):
            entries = intake.read(f)
            pending_count += sum(1 for e in entries if e.status == "pending")
        if pending_count:
            lines.append(f"Pending intake items: {pending_count}")
    except Exception:
        pass

    lines.append("Session rules: read _resume.md -> _intake_*.md -> _aware_*.md -> _scratchpad.md -> _living_decisions.md, then work.")
    return " | ".join(lines)
