"""Tests for src/devlead/project_init.py.

Part of FEATURES-0015 (Phase 1 BO-2). Verifies:
  - interview() runs through all 10 questions with mocked I/O
  - write_answers produces parseable Markdown
  - hash_hierarchy is stable across whitespace edits
  - lock_hierarchy is idempotent on same hash
  - generate_intake_from_ttos splits by ttype correctly
"""
from __future__ import annotations

from pathlib import Path

from devlead.hierarchy import BO, TBO, TTO, Sprint
from devlead.project_init import (
    ANSWERS_FILENAME,
    QUESTIONS,
    generate_intake_from_ttos,
    hash_hierarchy,
    interview,
    lock_hierarchy,
    write_answers,
)


# --- interview -------------------------------------------------------------

def test_interview_collects_all_answers():
    """All 10 questions get prompted and answers stored under their keys."""
    scripted = iter([
        "A Slack-digest Chrome extension",
        "2026-05-15",
        "50 installs",
        "cleaner",
        "scope-creep",
        "Claude Code",
        "weekly",
        "depends",
        "trial signups",
        "manual",
    ])
    outputs: list[str] = []
    answers = interview(input_fn=lambda _: next(scripted), output_fn=outputs.append)
    assert set(answers.keys()) == {q.key for q in QUESTIONS}
    assert answers["project_pitch"] == "A Slack-digest Chrome extension"
    assert answers["next_release_date"] == "2026-05-15"
    assert answers["win_metric"] == "trial signups"
    assert answers["metric_source"] == "manual"


def test_interview_strips_whitespace():
    scripted = iter(["  trimmed answer  "] * len(QUESTIONS))
    answers = interview(
        input_fn=lambda _: next(scripted),
        output_fn=lambda _: None,
    )
    assert answers["project_pitch"] == "trimmed answer"


def test_interview_empty_answer_kept_as_empty_string():
    scripted = iter([""] * len(QUESTIONS))
    answers = interview(
        input_fn=lambda _: next(scripted),
        output_fn=lambda _: None,
    )
    assert all(v == "" for v in answers.values())


def test_interview_outputs_round_headers():
    """Each round transition emits a header line so the user can pace themselves."""
    scripted = iter(["a"] * len(QUESTIONS))
    outputs: list[str] = []
    interview(input_fn=lambda _: next(scripted), output_fn=outputs.append)
    joined = "\n".join(outputs)
    # 4 distinct round labels should each appear at least once
    rounds = {q.round_label for q in QUESTIONS}
    assert len(rounds) == 4
    for r in rounds:
        assert r in joined


# --- write_answers --------------------------------------------------------

def test_write_answers_creates_file_with_all_keys(tmp_path: Path):
    answers = {q.key: f"answer-{q.key}" for q in QUESTIONS}
    path = tmp_path / ANSWERS_FILENAME
    write_answers(answers, path)
    text = path.read_text(encoding="utf-8")
    for q in QUESTIONS:
        assert q.key in text
        assert f"answer-{q.key}" in text


def test_write_answers_includes_suggested_prompt(tmp_path: Path):
    """Output must include a Claude-pastable prompt to bridge to the next step."""
    path = tmp_path / ANSWERS_FILENAME
    write_answers({}, path)  # empty answers fine
    text = path.read_text(encoding="utf-8")
    assert "Suggested prompt for Claude" in text
    assert "_project_hierarchy.md" in text
    assert "devlead project-init lock" in text


def test_write_answers_handles_missing_keys_with_placeholder(tmp_path: Path):
    path = tmp_path / ANSWERS_FILENAME
    write_answers({}, path)  # nothing supplied
    text = path.read_text(encoding="utf-8")
    assert "(no answer)" in text


def test_write_answers_creates_parent_dir(tmp_path: Path):
    path = tmp_path / "nested" / "subdir" / ANSWERS_FILENAME
    write_answers({"project_pitch": "x"}, path)
    assert path.exists()


# --- hash_hierarchy -------------------------------------------------------

def test_hash_hierarchy_stable_across_whitespace_changes(tmp_path: Path):
    p1 = tmp_path / "h1.md"
    p2 = tmp_path / "h2.md"
    p1.write_text("# Hierarchy\n\n## Sprint 1\n", encoding="utf-8")
    p2.write_text("# Hierarchy   \n\n\n\n## Sprint 1\n", encoding="utf-8")  # extra blanks + trailing space
    assert hash_hierarchy(p1) == hash_hierarchy(p2)


def test_hash_hierarchy_changes_on_real_content_change(tmp_path: Path):
    p1 = tmp_path / "h1.md"
    p2 = tmp_path / "h2.md"
    p1.write_text("# A\n", encoding="utf-8")
    p2.write_text("# B\n", encoding="utf-8")
    assert hash_hierarchy(p1) != hash_hierarchy(p2)


def test_hash_hierarchy_returns_12_chars(tmp_path: Path):
    p = tmp_path / "h.md"
    p.write_text("# anything\n", encoding="utf-8")
    h = hash_hierarchy(p)
    assert len(h) == 12
    assert all(c in "0123456789abcdef" for c in h)


# --- lock_hierarchy -------------------------------------------------------

def test_lock_hierarchy_writes_decision_entry(tmp_path: Path):
    h_path = tmp_path / "_project_hierarchy.md"
    d_path = tmp_path / "_living_decisions.md"
    h_path.write_text("# Hierarchy\n\n## Sprint 1\n", encoding="utf-8")
    h = lock_hierarchy(h_path, d_path)
    text = d_path.read_text(encoding="utf-8")
    assert h in text
    assert "Hierarchy locked" in text
    assert "**Status:** locked" in text


def test_lock_hierarchy_idempotent_on_same_hash(tmp_path: Path):
    h_path = tmp_path / "_project_hierarchy.md"
    d_path = tmp_path / "_living_decisions.md"
    h_path.write_text("# Hierarchy\n\n## Sprint 1\n", encoding="utf-8")
    h1 = lock_hierarchy(h_path, d_path)
    h2 = lock_hierarchy(h_path, d_path)
    assert h1 == h2
    text = d_path.read_text(encoding="utf-8")
    # Hash should appear only once in the decisions file
    assert text.count(f"`{h1}`") == 1


def test_lock_hierarchy_writes_new_entry_when_hash_changes(tmp_path: Path):
    h_path = tmp_path / "_project_hierarchy.md"
    d_path = tmp_path / "_living_decisions.md"
    h_path.write_text("# Hierarchy v1\n", encoding="utf-8")
    h1 = lock_hierarchy(h_path, d_path)
    h_path.write_text("# Hierarchy v2 — substantially different\n", encoding="utf-8")
    h2 = lock_hierarchy(h_path, d_path)
    assert h1 != h2
    text = d_path.read_text(encoding="utf-8")
    assert h1 in text
    assert h2 in text


def test_lock_hierarchy_with_note(tmp_path: Path):
    h_path = tmp_path / "_project_hierarchy.md"
    d_path = tmp_path / "_living_decisions.md"
    h_path.write_text("# H\n", encoding="utf-8")
    lock_hierarchy(h_path, d_path, note="MVP cut-off after round 2 review")
    text = d_path.read_text(encoding="utf-8")
    assert "MVP cut-off after round 2 review" in text


# --- generate_intake_from_ttos --------------------------------------------

def _sample_sprints() -> list[Sprint]:
    """Mixed functional + non-functional TTOs across two TBOs."""
    f1 = TTO(id="TTO-1", name="Func A", weight=20, done=False, ttype="functional")
    f2 = TTO(id="TTO-2", name="Func B", weight=30, done=True, ttype="functional",
             intent_vector={"BO-1": 0.4})
    nf1 = TTO(id="TTO-3", name="NonFunc A", weight=25, done=False, ttype="non-functional")
    tbo = TBO(id="TBO-1", name="Theme", weight=100, ttos=[f1, f2, nf1])
    bo = BO(id="BO-1", name="Objective", weight=50, tbos=[tbo])
    return [Sprint(name="S1", bos=[bo])]


def test_generate_intake_writes_two_files(tmp_path: Path):
    sprints = _sample_sprints()
    counts = generate_intake_from_ttos(sprints, tmp_path)
    assert "_intake_hierarchy_features.md" in counts
    assert "_intake_hierarchy_nonfunctional.md" in counts
    assert (tmp_path / "_intake_hierarchy_features.md").exists()
    assert (tmp_path / "_intake_hierarchy_nonfunctional.md").exists()


def test_generate_intake_splits_by_ttype(tmp_path: Path):
    sprints = _sample_sprints()
    counts = generate_intake_from_ttos(sprints, tmp_path)
    assert counts["_intake_hierarchy_features.md"] == 2     # 2 functional TTOs
    assert counts["_intake_hierarchy_nonfunctional.md"] == 1


def test_generate_intake_includes_intent_vector(tmp_path: Path):
    sprints = _sample_sprints()
    generate_intake_from_ttos(sprints, tmp_path)
    text = (tmp_path / "_intake_hierarchy_features.md").read_text(encoding="utf-8")
    assert "BO-1: 0.4" in text  # intent_vector serialised


def test_generate_intake_marks_done_status_correctly(tmp_path: Path):
    sprints = _sample_sprints()
    generate_intake_from_ttos(sprints, tmp_path)
    func_text = (tmp_path / "_intake_hierarchy_features.md").read_text(encoding="utf-8")
    # Func A is not done, Func B is done — both should be present
    assert "Func A" in func_text
    assert "Func B" in func_text
    # Status reflects done flag
    assert "**Status:** pending" in func_text  # Func A
    assert "**Status:** done" in func_text     # Func B


def test_generate_intake_is_idempotent_overwrite(tmp_path: Path):
    sprints = _sample_sprints()
    generate_intake_from_ttos(sprints, tmp_path)
    size1 = (tmp_path / "_intake_hierarchy_features.md").stat().st_size
    # Second run with same data — file size unchanged (modulo timestamps)
    generate_intake_from_ttos(sprints, tmp_path)
    size2 = (tmp_path / "_intake_hierarchy_features.md").stat().st_size
    # Allow small drift from timestamps but should be very close
    assert abs(size1 - size2) < 200


def test_generate_intake_handles_empty_hierarchy(tmp_path: Path):
    counts = generate_intake_from_ttos([], tmp_path)
    assert counts["_intake_hierarchy_features.md"] == 0
    assert counts["_intake_hierarchy_nonfunctional.md"] == 0
