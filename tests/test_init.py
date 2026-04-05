"""Tests for devlead init — scaffold, hook config, gitignore."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from devlead.init import do_init


def test_init_creates_claude_docs(tmp_path):
    """init creates claude_docs/ directory."""
    do_init(tmp_path)
    assert (tmp_path / "claude_docs").is_dir()


def test_init_creates_all_doc_files(tmp_path):
    """init creates all expected markdown files."""
    do_init(tmp_path)
    docs = tmp_path / "claude_docs"
    expected = [
        "_project_status.md",
        "_project_tasks.md",
        "_project_roadmap.md",
        "_intake_bugs.md",
        "_intake_features.md",
        "_intake_gaps.md",
        "_intake_changes.md",
        "_living_standing_instructions.md",
    ]
    for fname in expected:
        assert (docs / fname).exists(), f"Missing: {fname}"


def test_init_creates_devlead_toml(tmp_path):
    """init creates devlead.toml with project name."""
    do_init(tmp_path)
    toml_path = tmp_path / "devlead.toml"
    assert toml_path.exists()
    content = toml_path.read_text()
    assert "[project]" in content
    assert "docs_dir" in content


def test_init_merges_hooks(tmp_path):
    """init creates .claude/settings.json with hooks."""
    do_init(tmp_path)
    settings_path = tmp_path / ".claude" / "settings.json"
    assert settings_path.exists()
    settings = json.loads(settings_path.read_text())
    assert "hooks" in settings
    assert "SessionStart" in settings["hooks"]
    assert "PreToolUse" in settings["hooks"]


def test_init_preserves_existing_hooks(tmp_path):
    """init merges hooks without overwriting existing ones."""
    # Pre-existing settings
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    existing = {
        "hooks": {
            "PreToolUse": [
                {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}
            ]
        },
        "other_setting": True,
    }
    (claude_dir / "settings.json").write_text(json.dumps(existing))

    do_init(tmp_path)

    settings = json.loads((claude_dir / "settings.json").read_text())
    # Existing PreToolUse hooks preserved + new ones added
    assert settings["other_setting"] is True
    pre_tool = settings["hooks"]["PreToolUse"]
    matchers = [h.get("matcher", "") for h in pre_tool]
    assert "Bash" in matchers  # preserved
    assert "Edit|Write" in matchers  # added


def test_init_adds_gitignore_entry(tmp_path):
    """init adds session_state.json to .gitignore."""
    do_init(tmp_path)
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert "session_state.json" in gitignore.read_text()


def test_init_preserves_existing_gitignore(tmp_path):
    """init appends to existing .gitignore."""
    (tmp_path / ".gitignore").write_text("node_modules/\n")
    do_init(tmp_path)
    content = (tmp_path / ".gitignore").read_text()
    assert "node_modules/" in content
    assert "session_state.json" in content


def test_init_idempotent(tmp_path):
    """Running init twice doesn't duplicate files or entries."""
    do_init(tmp_path)
    do_init(tmp_path)

    # .gitignore shouldn't have duplicate entries
    content = (tmp_path / ".gitignore").read_text()
    assert content.count("session_state.json") == 1

    # Files still exist
    assert (tmp_path / "claude_docs" / "_project_tasks.md").exists()


def test_init_skips_existing_docs(tmp_path):
    """init doesn't overwrite existing doc files."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    custom_content = "# My Custom Tasks\nDo not overwrite me.\n"
    (docs / "_project_tasks.md").write_text(custom_content)

    do_init(tmp_path)

    assert (docs / "_project_tasks.md").read_text() == custom_content


def test_init_cli(tmp_path):
    """devlead init works from CLI."""
    result = subprocess.run(
        [sys.executable, "-m", "devlead", "init"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert (tmp_path / "claude_docs").is_dir()
