"""Tests for collab.py — cross-project collaboration channel."""

import subprocess
import sys
from pathlib import Path

import pytest

from devlead.collab import (
    init_collab,
    scan_inbox,
    parse_collab_file,
    collab_status,
)


def test_init_collab(tmp_path):
    """init_collab creates .collab/INBOX/ and .collab/OUTBOX/."""
    init_collab(tmp_path)
    assert (tmp_path / ".collab" / "INBOX").is_dir()
    assert (tmp_path / ".collab" / "OUTBOX").is_dir()


def test_init_collab_idempotent(tmp_path):
    """init_collab can be called twice."""
    init_collab(tmp_path)
    init_collab(tmp_path)
    assert (tmp_path / ".collab" / "INBOX").is_dir()


def test_scan_inbox_empty(tmp_path):
    """Empty inbox returns empty list."""
    init_collab(tmp_path)
    items = scan_inbox(tmp_path)
    assert items == []


def test_scan_inbox_finds_requests(tmp_path):
    """scan_inbox finds .md files in INBOX."""
    init_collab(tmp_path)
    inbox = tmp_path / ".collab" / "INBOX"
    (inbox / "REQUEST_projA_001.md").write_text(
        "# REQUEST: Need API endpoint\n\n> From: projA\n> Status: OPEN\n"
    )
    items = scan_inbox(tmp_path)
    assert len(items) == 1
    assert items[0]["filename"] == "REQUEST_projA_001.md"


def test_parse_collab_file():
    """parse_collab_file extracts metadata."""
    content = (
        "# REQUEST: Batch support\n\n"
        "> From: eTrading\n"
        "> To: income_desk\n"
        "> Date: 2026-04-05\n"
        "> Priority: P1\n"
        "> Status: OPEN\n"
    )
    meta = parse_collab_file(content)
    assert meta["type"] == "REQUEST"
    assert meta["title"] == "Batch support"
    assert meta["from"] == "eTrading"
    assert meta["to"] == "income_desk"
    assert meta["status"] == "OPEN"
    assert meta["priority"] == "P1"


def test_parse_collab_file_feedback():
    """parse_collab_file handles FEEDBACK type."""
    content = "# FEEDBACK: API ready\n\n> From: income_desk\n> Status: CLOSED\n"
    meta = parse_collab_file(content)
    assert meta["type"] == "FEEDBACK"
    assert meta["status"] == "CLOSED"


def test_collab_status(tmp_path):
    """collab_status summarizes inbox/outbox."""
    init_collab(tmp_path)
    inbox = tmp_path / ".collab" / "INBOX"
    outbox = tmp_path / ".collab" / "OUTBOX"
    (inbox / "REQUEST_001.md").write_text("# REQUEST: Test\n> Status: OPEN\n")
    (outbox / "FEEDBACK_001.md").write_text("# FEEDBACK: Done\n> Status: CLOSED\n")

    status = collab_status(tmp_path)
    assert status["inbox_count"] == 1
    assert status["outbox_count"] == 1


def test_collab_cli_status(tmp_path):
    """devlead collab status runs without crash."""
    result = subprocess.run(
        [sys.executable, "-m", "devlead", "collab", "status"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
