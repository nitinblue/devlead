"""Tests for effort tracking wired into gate.check_pretooluse.

Part of FEATURES-0016 (Phase 1 BO-3). Verifies:
  - PreToolUse on a non-exempt file with active CWI writes effort entries
  - PreToolUse on an exempt file does NOT write effort entries
  - PreToolUse with no CWI does NOT write effort entries (gate blocks instead)
  - Multiple CWIs produce one effort row per CWI per call
  - Aggregation by tto_id works for synthetic intake-style IDs
"""
from __future__ import annotations

from pathlib import Path

import pytest

from devlead import effort, gate


def _scaffold_devlead_docs(tmp_path: Path, in_progress_ids: list[str] = ()) -> Path:
    """Build a minimal devlead_docs/ tree with optional in_progress intake entries."""
    docs = tmp_path / "devlead_docs"
    docs.mkdir(parents=True, exist_ok=True)

    # devlead.toml — minimal, default exempt paths kick in
    (tmp_path / "devlead.toml").write_text("", encoding="utf-8")

    # Empty audit log so audit.append_event won't error
    (docs / "_audit_log.jsonl").write_text("", encoding="utf-8")

    # Intake file with optional in_progress entries
    intake_lines = ["# _intake_features.md\n\n## Entries\n"]
    for i, eid in enumerate(in_progress_ids, start=1):
        intake_lines.append(
            f"\n## {eid} - test entry {i}\n"
            f"- **Source:** test\n"
            f"- **Captured:** 2026-04-17T00:00:00Z\n"
            f"- **Summary:** test\n"
            f"- **Actionable items:**\n"
            f"  - (none)\n"
            f"- **Status:** in_progress\n"
            f"- **Origin:** normal\n"
            f"- **Promoted to:** (pending)\n"
            f"- **Promoted at:** (pending)\n"
        )
    (docs / "_intake_features.md").write_text("".join(intake_lines), encoding="utf-8")
    return docs


def _hook_input(file_path: str, tool: str = "Edit") -> dict:
    return {"tool_name": tool, "tool_input": {"file_path": file_path}}


def test_gate_pass_writes_effort_row_per_cwi(tmp_path: Path):
    docs = _scaffold_devlead_docs(tmp_path, in_progress_ids=["FEATURES-0016"])
    src_file = tmp_path / "src" / "app.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("# stub\n", encoding="utf-8")

    result = gate.check_pretooluse(_hook_input(str(src_file)), tmp_path)
    assert result == {"continue": True}

    rows = effort.get_all_effort(docs)
    assert "FEATURES-0016" in rows
    assert rows["FEATURES-0016"]["total_tokens"] == 0  # tokens unknown for now
    # _aggregate forces sessions to at least 1; what we care about is row count via log read
    log = docs / "_effort_log.jsonl"
    assert len(log.read_text(encoding="utf-8").strip().splitlines()) == 1


def test_gate_pass_writes_one_row_per_cwi_with_multiple_focuses(tmp_path: Path):
    docs = _scaffold_devlead_docs(
        tmp_path, in_progress_ids=["FEATURES-0014", "FEATURES-0016"],
    )
    src_file = tmp_path / "src" / "x.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("\n", encoding="utf-8")

    gate.check_pretooluse(_hook_input(str(src_file)), tmp_path)

    log = docs / "_effort_log.jsonl"
    rows = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 2  # one per CWI
    contents = "\n".join(rows)
    assert "FEATURES-0014" in contents
    assert "FEATURES-0016" in contents


def test_gate_exempt_path_does_NOT_write_effort(tmp_path: Path):
    """Editing devlead_docs/ or tests/ — exempt — must not pollute effort log."""
    docs = _scaffold_devlead_docs(tmp_path, in_progress_ids=["FEATURES-0016"])
    md_file = tmp_path / "README.md"
    md_file.write_text("# x\n", encoding="utf-8")

    gate.check_pretooluse(_hook_input(str(md_file)), tmp_path)

    log = docs / "_effort_log.jsonl"
    # Exempt path => no effort row written
    assert not log.exists() or log.read_text(encoding="utf-8").strip() == ""


def test_gate_no_cwi_does_NOT_write_effort(tmp_path: Path, monkeypatch):
    """When discipline is broken (no in_progress entry), gate writes a block
    event but NOT an effort row — effort is per-TTO accounting, not blame."""
    docs = _scaffold_devlead_docs(tmp_path, in_progress_ids=[])
    src_file = tmp_path / "src" / "x.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("\n", encoding="utf-8")

    # The block path may sys.exit in hard mode; default config is hard, but
    # without devlead.toml override the default is hard. Catch SystemExit.
    try:
        gate.check_pretooluse(_hook_input(str(src_file)), tmp_path)
    except SystemExit:
        pass  # Expected when enforcement_mode != warn

    log = docs / "_effort_log.jsonl"
    assert not log.exists() or log.read_text(encoding="utf-8").strip() == ""


def test_repeated_edits_accumulate_per_tto(tmp_path: Path):
    docs = _scaffold_devlead_docs(tmp_path, in_progress_ids=["FEATURES-0016"])
    src_file = tmp_path / "src" / "x.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("\n", encoding="utf-8")

    for _ in range(5):
        gate.check_pretooluse(_hook_input(str(src_file)), tmp_path)

    log = docs / "_effort_log.jsonl"
    rows = log.read_text(encoding="utf-8").strip().splitlines()
    assert len(rows) == 5
    aggregate = effort.get_all_effort(docs)
    assert "FEATURES-0016" in aggregate


def test_effort_proxy_count_via_get_all_effort(tmp_path: Path):
    """v1 proxy: token sum is 0 for every row, but row-count == edit-count.
    Surface that separately so dashboard can show 'edits per TTO'."""
    docs = _scaffold_devlead_docs(tmp_path, in_progress_ids=["FEATURES-0016"])
    src_file = tmp_path / "src" / "x.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("\n", encoding="utf-8")
    for _ in range(3):
        gate.check_pretooluse(_hook_input(str(src_file)), tmp_path)

    log = docs / "_effort_log.jsonl"
    raw_rows = log.read_text(encoding="utf-8").strip().splitlines()
    # Row count is the v1 proxy for edit count per TTO
    assert len(raw_rows) == 3
