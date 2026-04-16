# tests/test_collab_pipeline.py
"""Tests for strengthened collab pipeline."""

import pytest
from pathlib import Path
from devlead.collab import (
    create_change_request,
    create_issue_escalation,
    create_status_update,
    create_feedback,
    parse_collab_file,
    scan_inbox,
    sync_outbox_to_inbox,
)


COLLAB_TYPES = ["CHANGE_REQUEST", "ISSUE_ESCALATION", "STATUS_UPDATE", "FEEDBACK"]


def test_create_change_request(tmp_path):
    """Create a structured change request in OUTBOX."""
    outbox = tmp_path / ".collab" / "OUTBOX"
    outbox.mkdir(parents=True)
    path = create_change_request(
        project_dir=tmp_path,
        to_project="income_desk",
        title="Need batch support for multi-leg",
        body="batch_reprice() must handle multi-leg trades.",
        priority="P1",
        blocks="TASK-045",
    )
    assert path.exists()
    content = path.read_text()
    assert "CHANGE_REQUEST" in content
    assert "income_desk" in content
    assert "P1" in content
    assert "TASK-045" in content


def test_create_issue_escalation(tmp_path):
    outbox = tmp_path / ".collab" / "OUTBOX"
    outbox.mkdir(parents=True)
    path = create_issue_escalation(
        project_dir=tmp_path,
        to_project="eTrading",
        title="Rate limit bug affects us",
        body="ISS-004 in our project is caused by eTrading API.",
        priority="P1",
    )
    assert path.exists()
    content = path.read_text()
    assert "ISSUE_ESCALATION" in content


def test_create_status_update(tmp_path):
    outbox = tmp_path / ".collab" / "OUTBOX"
    outbox.mkdir(parents=True)
    path = create_status_update(
        project_dir=tmp_path,
        to_project="eTrading",
        title="Batch support is live",
        body="batch_reprice() now handles multi-leg. Closes REQUEST-001.",
    )
    assert path.exists()
    content = path.read_text()
    assert "STATUS_UPDATE" in content


def test_create_feedback(tmp_path):
    outbox = tmp_path / ".collab" / "OUTBOX"
    outbox.mkdir(parents=True)
    path = create_feedback(
        project_dir=tmp_path,
        to_project="eTrading",
        title="Re: batch support request",
        body="We can do this but need 2 weeks.",
        references="REQUEST_eTrading_001.md",
    )
    assert path.exists()
    content = path.read_text()
    assert "FEEDBACK" in content
    assert "REQUEST_eTrading_001.md" in content


def test_parse_all_types():
    """parse_collab_file handles all message types."""
    for msg_type in COLLAB_TYPES:
        content = f"# {msg_type}: Test title\n\n> From: proj_a\n> To: proj_b\n> Status: OPEN\n"
        meta = parse_collab_file(content)
        assert meta["type"] == msg_type


def test_sync_outbox_to_inbox(tmp_path):
    """sync copies OUTBOX files to target project INBOX."""
    proj_a = tmp_path / "proj_a"
    proj_b = tmp_path / "proj_b"
    (proj_a / ".collab" / "OUTBOX").mkdir(parents=True)
    (proj_b / ".collab" / "INBOX").mkdir(parents=True)

    # Create a request in A's outbox targeted at B
    outbox_file = proj_a / ".collab" / "OUTBOX" / "CHANGE_REQUEST_proj_b_001.md"
    outbox_file.write_text(
        "# CHANGE_REQUEST: Test\n\n> From: proj_a\n> To: proj_b\n> Status: OPEN\n"
    )

    synced = sync_outbox_to_inbox(proj_a, {"proj_b": proj_b})
    assert synced == 1
    assert (proj_b / ".collab" / "INBOX" / "CHANGE_REQUEST_proj_b_001.md").exists()


def test_sync_skips_already_synced(tmp_path):
    """sync doesn't copy files that already exist in target INBOX."""
    proj_a = tmp_path / "proj_a"
    proj_b = tmp_path / "proj_b"
    (proj_a / ".collab" / "OUTBOX").mkdir(parents=True)
    (proj_b / ".collab" / "INBOX").mkdir(parents=True)

    outbox_file = proj_a / ".collab" / "OUTBOX" / "CR_proj_b_001.md"
    outbox_file.write_text("# CHANGE_REQUEST: Test\n> To: proj_b\n")
    # Already in inbox
    (proj_b / ".collab" / "INBOX" / "CR_proj_b_001.md").write_text("exists")

    synced = sync_outbox_to_inbox(proj_a, {"proj_b": proj_b})
    assert synced == 0
