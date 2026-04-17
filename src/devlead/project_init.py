"""project-init CLI — cold-start onboarding for a new DevLead project.

The 10-question interview captures structured answers from the user about a
project (what it ships, when, what success looks like, what metric to track).
Answers are written to `devlead_docs/_project_init_answers.md` as structured
Markdown that Claude (or another LLM in the user's session) can read and
draft a Vision + 4 BOs + TBOs + TTOs from. DevLead does NOT embed an LLM
call — the drafting is performed by the LLM the user is already using.
That keeps DevLead dependency-free.

After the user (or Claude) populates `_project_hierarchy.md`, the `lock`
subcommand:
  - hashes the hierarchy file (sha256 of normalised content)
  - appends a lock entry to `_living_decisions.md`
  - generates `_intake_features.md` and `_intake_nonfunctional.md` from the
    parsed TTOs, split by `ttype`

Public API:
  - QUESTIONS — the 10 interview questions in 4 rounds
  - interview(input_fn, output_fn) -> dict[str, str]
  - write_answers(answers, path)
  - lock_hierarchy(hierarchy_path, decisions_path) -> str (the hash)
  - generate_intake_from_ttos(sprints, intake_dir) -> dict[str, int]

Part of FEATURES-0015 (Phase 1 BO-2). Vision Tab 5 spec.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from devlead.hierarchy import Sprint, parse

ANSWERS_FILENAME = "_project_init_answers.md"


@dataclass(frozen=True)
class Question:
    key: str        # snake_case identifier used in the answers file
    round_label: str
    prompt: str


# 10 questions in 4 rounds — matches Tab 5's "How DevLead generates this hierarchy" cards.
QUESTIONS: list[Question] = [
    Question("project_pitch",      "1 — what you ship",      "In one line, what does this project ship?"),
    Question("next_release_date",  "1 — what you ship",      "When is your next release / milestone? (date, e.g. 2026-05-15)"),
    Question("release_outcome",    "1 — what you ship",      "What's the one outcome that release should produce?"),
    Question("speed_vs_quality",   "2 — release pain",       "Ship faster or ship cleaner this release? [faster/cleaner]"),
    Question("release_pain",       "2 — release pain",       "What breaks most releases for you? (one word)"),
    Question("ai_tools",           "3 — AI in your loop",    "Claude Code / Cursor / Aider / none? (comma-separated)"),
    Question("ai_drift_frequency", "3 — AI in your loop",    "Has AI ever shipped something you didn't ask for? [no/sometimes/weekly]"),
    Question("trust_done",         "3 — AI in your loop",    "Do you trust 'done' today? [yes/no/depends]"),
    Question("win_metric",         "4 — what you can measure", "One number that, if it moved this release, would mean win."),
    Question("metric_source",      "4 — what you can measure", "Where does that number live? [URL / shell command / 'manual']"),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def interview(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> dict[str, str]:
    """Run the 10-question interactive interview. Returns {key: answer} dict.

    Both I/O callables are injectable for testability — pass a script of
    answers in tests.
    """
    output_fn("DevLead project-init — let me draft your hierarchy.")
    output_fn("Ten questions, four rounds, ~10 minutes.\n")
    answers: dict[str, str] = {}
    current_round = ""
    for q in QUESTIONS:
        if q.round_label != current_round:
            output_fn(f"\n--- Round {q.round_label} ---")
            current_round = q.round_label
        ans = input_fn(f"  {q.prompt}\n  > ").strip()
        answers[q.key] = ans
    return answers


def write_answers(answers: dict[str, str], path: Path) -> None:
    """Write the captured answers to a structured Markdown file.

    The format is parseable by Claude (or any LLM) and gives the LLM enough
    context to draft a Vision + 4 BOs + TBOs + TTOs.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project init answers",
        "",
        f"<!-- Captured by `devlead project-init` at {_now_iso()}. -->",
        "<!-- Next: paste the prompt below into Claude/Cursor/etc to draft the hierarchy. -->",
        "",
    ]
    current_round = ""
    for q in QUESTIONS:
        if q.round_label != current_round:
            lines.append(f"## Round {q.round_label}")
            lines.append("")
            current_round = q.round_label
        ans = answers.get(q.key, "").strip() or "(no answer)"
        lines.append(f"- **{q.key}** — _{q.prompt}_")
        lines.append(f"  > {ans}")
        lines.append("")
    lines.append("## Suggested prompt for Claude")
    lines.append("")
    lines.append("```")
    lines.append("Read devlead_docs/_project_init_answers.md.")
    lines.append("Draft a Vision sentence and 4 release-world Business Objectives")
    lines.append("(BOs) for this project. For each BO, define:")
    lines.append("  - one-line pain it ends")
    lines.append("  - metric (the number that proves it)")
    lines.append("  - baseline & target values")
    lines.append("  - metric_source (URL / shell command / manual)")
    lines.append("  - deadline")
    lines.append("  - weight (priority share, sum to 1.0 across BOs)")
    lines.append("Then break each BO into 1-3 TBOs (themes), and each TBO into")
    lines.append("3-5 TTOs split between functional and non-functional.")
    lines.append("Write the result to devlead_docs/_project_hierarchy.md following")
    lines.append("the existing format. When done, run: devlead project-init lock")
    lines.append("```")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _normalise_for_hash(text: str) -> str:
    """Strip trailing whitespace per line + collapse blank-line runs.

    Hash is meant to detect *meaningful* content changes, not whitespace edits.
    """
    out_lines: list[str] = []
    blank_run = 0
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        out_lines.append(line)
    return "\n".join(out_lines)


def hash_hierarchy(hierarchy_path: Path) -> str:
    """sha256 of normalised hierarchy content. 12-char hex prefix returned."""
    text = Path(hierarchy_path).read_text(encoding="utf-8")
    h = hashlib.sha256(_normalise_for_hash(text).encode("utf-8")).hexdigest()
    return h[:12]


def lock_hierarchy(
    hierarchy_path: Path,
    decisions_path: Path,
    *,
    note: str = "",
) -> str:
    """Hash the hierarchy and append a lock entry to _living_decisions.md.

    Returns the hash. Idempotency: if the most recent entry in decisions
    already has the same hash, no new entry is written (silent no-op).
    """
    hierarchy_path = Path(hierarchy_path)
    decisions_path = Path(decisions_path)
    h = hash_hierarchy(hierarchy_path)

    # Idempotency: skip if the same hash appears in the recent tail.
    existing = decisions_path.read_text(encoding="utf-8") if decisions_path.exists() else ""
    last_tail = "\n".join(existing.splitlines()[-30:])
    if f"`{h}`" in last_tail:
        return h

    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    entry_lines = [
        "",
        f"## {datetime.now(timezone.utc).strftime('%Y-%m-%d')} - Hierarchy locked",
        f"- **Decision:** Project hierarchy frozen as MVP baseline.",
        f"- **Hash:** `{h}` (sha256 prefix of normalised `_project_hierarchy.md`)",
        f"- **Locked at:** {_now_iso()}",
        f"- **Status:** locked",
    ]
    if note:
        entry_lines.append(f"- **Note:** {note}")

    with open(decisions_path, "a", encoding="utf-8") as f:
        f.write("\n".join(entry_lines) + "\n")
    return h


# --- intake generation ----------------------------------------------------


def _intake_entry_md(idx: int, prefix: str, tto, parent_label: str) -> str:
    """Render a single TTO as an intake entry."""
    eid = f"{prefix}-{idx:04d}"
    intent_str = ""
    if tto.intent_vector:
        intent_str = ", ".join(f"{k}: {v}" for k, v in tto.intent_vector.items())
    return (
        f"## {eid} - {tto.name}\n"
        f"- **Source:** _project_hierarchy.md ({parent_label} / {tto.id})\n"
        f"- **Captured:** {_now_iso()}\n"
        f"- **Summary:** {tto.name}\n"
        f"- **Actionable items:**\n"
        f"  - [{'x' if tto.done else ' '}] {tto.name}\n"
        f"- **Proposed BO:** ({parent_label})\n"
        f"- **Proposed Sprint:** (per hierarchy)\n"
        f"- **Proposed weight:** {tto.weight}\n"
        f"- **Status:** {'done' if tto.done else 'pending'}\n"
        f"- **Origin:** generated\n"
        f"- **Intent vector:** {intent_str or '(none)'}\n"
        f"- **Verify kind:** {tto.verify_kind}\n"
        f"- **Promoted to:** {tto.id}\n"
        f"- **Promoted at:** {_now_iso()}\n"
    )


def _intake_header(filename: str, ttype_label: str) -> str:
    """Header block for a generated intake file."""
    return (
        f"# {filename}\n\n"
        f"<!-- Auto-generated by `devlead project-init generate-intake` at {_now_iso()}. -->\n"
        f"<!-- Source: TTOs of type `{ttype_label}` from _project_hierarchy.md. -->\n"
        f"<!-- Hand-edits will be overwritten on next regeneration. -->\n\n"
        f"## Entries\n\n"
    )


def generate_intake_from_ttos(
    sprints: list[Sprint],
    intake_dir: Path,
) -> dict[str, int]:
    """Walk the hierarchy and emit intake files split by TTO ttype.

    Writes:
      - _intake_features.md       (functional TTOs)
      - _intake_nonfunctional.md  (non-functional TTOs)

    Returns: {filename: entry_count} for what was written.

    NOTE: This OVERWRITES the target files. Intentional — these files are
    derived views of the hierarchy. Hand-edits don't survive. (The actual
    work-tracking intake entries live in user-managed _intake_*.md files
    with different IDs; this generator is for hierarchy-derived intake only.)
    """
    intake_dir = Path(intake_dir)
    intake_dir.mkdir(parents=True, exist_ok=True)
    func_entries: list[str] = []
    nonfunc_entries: list[str] = []

    func_idx = 0
    nf_idx = 0
    for s in sprints:
        for bo in s.bos:
            for tbo in bo.tbos:
                for tto in tbo.ttos:
                    parent = f"{bo.id} / {tbo.id}"
                    ttype = (tto.ttype or "functional").lower()
                    if "non" in ttype or ttype.startswith("nf"):
                        nf_idx += 1
                        nonfunc_entries.append(
                            _intake_entry_md(nf_idx, "HIERARCHY-NF", tto, parent)
                        )
                    else:
                        func_idx += 1
                        func_entries.append(
                            _intake_entry_md(func_idx, "HIERARCHY-F", tto, parent)
                        )

    counts: dict[str, int] = {}
    func_path = intake_dir / "_intake_hierarchy_features.md"
    nf_path = intake_dir / "_intake_hierarchy_nonfunctional.md"
    func_path.write_text(
        _intake_header("intake_hierarchy_features.md", "functional") + "\n".join(func_entries),
        encoding="utf-8",
    )
    nf_path.write_text(
        _intake_header("intake_hierarchy_nonfunctional.md", "non-functional") + "\n".join(nonfunc_entries),
        encoding="utf-8",
    )
    counts[func_path.name] = len(func_entries)
    counts[nf_path.name] = len(nonfunc_entries)
    return counts
