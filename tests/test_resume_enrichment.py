"""Tests for FEATURES-0017 anti-amnesia enrichment of resume.py.

Verifies the three new auto-derived sections:
  - Recently shipped (done intake entries within window)
  - Recent activity by intake (audit-log gate_pass grouped by cwi)
  - Untracked modules (modules in _aware_design.md not mentioned in intake)
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from devlead.resume import (
    _get_recent_active_cwi,
    _get_recent_done_intake,
    _get_untracked_modules,
    generate,
)


def _scaffold_docs(tmp_path: Path) -> Path:
    docs = tmp_path / "devlead_docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "_audit_log.jsonl").write_text("", encoding="utf-8")
    (docs / "_intake_features.md").write_text(
        "# _intake_features.md\n\n## Entries\n", encoding="utf-8"
    )
    return docs


def _write_intake_entry(
    docs: Path, eid: str, title: str, status: str, captured: str,
    intake_file: str = "_intake_features.md",
) -> None:
    """Append one entry to the intake file."""
    p = docs / intake_file
    block = (
        f"\n## {eid} - {title}\n"
        f"- **Source:** test\n"
        f"- **Captured:** {captured}\n"
        f"- **Summary:** {title}\n"
        f"- **Actionable items:**\n"
        f"  - (none)\n"
        f"- **Status:** {status}\n"
        f"- **Origin:** normal\n"
        f"- **Promoted to:** (pending)\n"
        f"- **Promoted at:** (pending)\n"
    )
    with open(p, "a", encoding="utf-8") as f:
        f.write(block)


def _write_audit_event(docs: Path, ts: str, cwi: list[str], file_path: str = "src/x.py") -> None:
    row = {
        "ts": ts, "event": "gate_pass", "tool": "Edit", "file": file_path,
        "cwi": cwi, "rule": "intake_trace", "result": "pass",
    }
    with open(docs / "_audit_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# --- _get_recent_done_intake ----------------------------------------------

def test_recent_done_intake_lists_only_done_within_window(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    today = datetime.now(timezone.utc)
    in_window = (today - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_window = (today - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_intake_entry(docs, "FEATURES-0001", "Recent done", "done", in_window)
    _write_intake_entry(docs, "FEATURES-0002", "Recent pending", "pending", in_window)
    _write_intake_entry(docs, "FEATURES-0003", "Old done", "done", out_window)

    lines = _get_recent_done_intake(docs, days=7)
    joined = "\n".join(lines)
    assert "FEATURES-0001" in joined
    assert "FEATURES-0002" not in joined  # not done
    assert "FEATURES-0003" not in joined  # outside window


def test_recent_done_intake_returns_placeholder_when_empty(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    lines = _get_recent_done_intake(docs)
    assert any("none in the last" in l for l in lines)


def test_recent_done_intake_sorts_newest_first(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    today = datetime.now(timezone.utc)
    older = (today - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    newer = (today - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_intake_entry(docs, "FEATURES-9001", "older", "done", older)
    _write_intake_entry(docs, "FEATURES-9002", "newer", "done", newer)
    lines = _get_recent_done_intake(docs)
    new_idx = next(i for i, l in enumerate(lines) if "FEATURES-9002" in l)
    old_idx = next(i for i, l in enumerate(lines) if "FEATURES-9001" in l)
    assert new_idx < old_idx


# --- _get_recent_active_cwi -----------------------------------------------

def test_recent_active_cwi_groups_and_counts(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for _ in range(3):
        _write_audit_event(docs, now_iso, ["FEATURES-0014"], "src/foo.py")
    for _ in range(5):
        _write_audit_event(docs, now_iso, ["FEATURES-0015"], "src/bar.py")
    lines = _get_recent_active_cwi(docs, days=7)
    joined = "\n".join(lines)
    assert "FEATURES-0014" in joined
    assert "FEATURES-0015" in joined
    # FEATURES-0015 has more activity (5) → should appear first
    f15_idx = next(i for i, l in enumerate(lines) if "FEATURES-0015" in l)
    f14_idx = next(i for i, l in enumerate(lines) if "FEATURES-0014" in l)
    assert f15_idx < f14_idx


def test_recent_active_cwi_excludes_old_events(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    old_iso = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    _write_audit_event(docs, old_iso, ["FEATURES-OLD"])
    lines = _get_recent_active_cwi(docs, days=7)
    assert any("no gated edits" in l for l in lines)


def test_recent_active_cwi_handles_missing_log(tmp_path: Path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    lines = _get_recent_active_cwi(docs)
    assert any("no audit log" in l for l in lines)


def test_recent_active_cwi_skips_malformed_lines(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(docs / "_audit_log.jsonl", "a", encoding="utf-8") as f:
        f.write("garbage line\n")
        f.write(json.dumps({
            "ts": now_iso, "event": "gate_pass", "result": "pass",
            "cwi": ["FEATURES-0014"], "file": "src/x.py",
        }) + "\n")
    lines = _get_recent_active_cwi(docs)
    assert "FEATURES-0014" in "\n".join(lines)


def test_recent_active_cwi_skips_non_pass_events(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(docs / "_audit_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": now_iso, "event": "gate_warn", "result": "warn", "cwi": ["FEATURES-X"],
        }) + "\n")
    lines = _get_recent_active_cwi(docs)
    assert any("no gated edits" in l for l in lines)


# --- _get_untracked_modules -----------------------------------------------

def test_untracked_modules_finds_modules_with_no_intake_mention(tmp_path: Path):
    docs = _scaffold_docs(tmp_path)
    (docs / "_aware_design.md").write_text(
        "# Modules\n\n"
        "### `devlead.foo`\n- Path: src/devlead/foo.py\n\n"
        "### `devlead.bar`\n- Path: src/devlead/bar.py\n",
        encoding="utf-8",
    )
    # foo is mentioned in intake; bar is not
    _write_intake_entry(docs, "FEATURES-0001", "Build the foo module", "done",
                        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    lines = _get_untracked_modules(docs)
    joined = "\n".join(lines)
    assert "bar" in joined
    assert "foo" not in joined


def test_untracked_modules_excludes_known_builtins(tmp_path: Path):
    """Modules predating FEATURES-NNNN tracking should not be flagged."""
    docs = _scaffold_docs(tmp_path)
    (docs / "_aware_design.md").write_text(
        "### `devlead.audit`\n\n### `devlead.cli`\n\n### `devlead.intake`\n",
        encoding="utf-8",
    )
    lines = _get_untracked_modules(docs)
    assert any("All" in l and "trace to an intake" in l for l in lines)


def test_untracked_modules_handles_missing_aware_file(tmp_path: Path):
    docs = tmp_path / "devlead_docs"
    docs.mkdir()
    lines = _get_untracked_modules(docs)
    assert any("no _aware_design.md" in l for l in lines)


# --- integration ----------------------------------------------------------

def test_generate_includes_all_three_new_sections(tmp_path: Path):
    """End-to-end: generate() must emit headers for all three new sections."""
    docs = _scaffold_docs(tmp_path)
    text = generate(tmp_path)
    assert "## Recently shipped (last 7 days)" in text
    assert "## Recent activity by intake (audit-derived)" in text
    assert "## Untracked modules (potential dark code)" in text


def test_generate_recently_shipped_appears_above_read_at_session_start(tmp_path: Path):
    """Layout intent: anti-amnesia sections come BEFORE the bookkeeping ones."""
    docs = _scaffold_docs(tmp_path)
    text = generate(tmp_path)
    shipped_pos = text.find("## Recently shipped")
    read_pos = text.find("## Read at session start")
    assert shipped_pos < read_pos
