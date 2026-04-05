# Audit Layer, Collab Pipeline & Rollover Policy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an audit layer that logs every file write with full context (who/where/when/why), strengthen the collab pipeline for cross-project change requests and feedback, and wire the configurable rollover trigger (date OR file size).

**Architecture:** The audit layer intercepts hook stdin JSON, extracts file_path + session context, and appends to `_audit_log.jsonl`. The collab pipeline adds structured message types (CHANGE_REQUEST, ISSUE_ESCALATION, STATUS_UPDATE, FEEDBACK) with auto-routing. Rollover adds a size-based trigger alongside the existing date trigger. All enforcement posture is configurable in `devlead.toml`.

**Tech Stack:** Python stdlib only (json, pathlib, sys, datetime, re)

**Spec:** Design agreed in brainstorming session 2026-04-05.

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `src/devlead/audit.py` | Create | Parse hook stdin, log writes, query log |
| `src/devlead/collab.py` | Modify | Add message types, create_request, create_feedback, sync between projects |
| `src/devlead/rollover.py` | Modify | Add size-based trigger check |
| `src/devlead/config.py` | Modify | Add `[audit]` and `[collab]` config sections |
| `src/devlead/state_machine.py` | Modify | Wire audit logging into `check_gate` |
| `src/devlead/cli.py` | Modify | Add `audit` subcommand, expand `collab` subcommands |
| `src/devlead/scaffold/hooks_settings.json` | Modify | Pass stdin to gate command |
| `src/devlead/scaffold/devlead_toml_template.toml` | Modify | Add audit + collab config |
| `tests/test_audit.py` | Create | Audit layer tests |
| `tests/test_collab_pipeline.py` | Create | Expanded collab tests |
| `tests/test_rollover_size.py` | Create | Size-based rollover tests |

---

## Task 1: audit.py — Parse Hook Stdin & Log Writes

**Files:**
- Create: `src/devlead/audit.py`
- Test: `tests/test_audit.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_audit.py
"""Tests for audit.py — hook stdin parsing and write logging."""

import json
import pytest
from pathlib import Path
from datetime import datetime
from devlead.audit import (
    parse_hook_stdin,
    log_write,
    read_audit_log,
    AuditEntry,
)


def test_parse_hook_stdin_edit():
    """Parse Edit tool stdin JSON."""
    stdin_json = json.dumps({
        "session_id": "sess-123",
        "cwd": "/home/user/project",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/home/user/project/src/main.py",
            "old_string": "foo",
            "new_string": "bar",
        },
        "hook_event_name": "PreToolUse",
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.session_id == "sess-123"
    assert entry.cwd == "/home/user/project"
    assert entry.tool_name == "Edit"
    assert entry.file_path == "/home/user/project/src/main.py"


def test_parse_hook_stdin_write():
    """Parse Write tool stdin JSON."""
    stdin_json = json.dumps({
        "session_id": "sess-456",
        "cwd": "/home/user/project",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/home/user/project/new_file.py",
            "content": "print('hello')",
        },
        "hook_event_name": "PreToolUse",
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.tool_name == "Write"
    assert entry.file_path == "/home/user/project/new_file.py"


def test_parse_hook_stdin_with_agent():
    """Parse stdin with subagent context."""
    stdin_json = json.dumps({
        "session_id": "sess-789",
        "cwd": "/home/user/project",
        "tool_name": "Edit",
        "tool_input": {"file_path": "/tmp/file.py"},
        "agent_id": "agent-abc",
        "agent_type": "Explore",
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.agent_id == "agent-abc"
    assert entry.agent_type == "Explore"


def test_parse_hook_stdin_no_file_path():
    """Non-file tools return None file_path."""
    stdin_json = json.dumps({
        "session_id": "sess-000",
        "cwd": "/home/user/project",
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
    })
    entry = parse_hook_stdin(stdin_json)
    assert entry.file_path is None


def test_parse_hook_stdin_bad_json():
    """Malformed JSON returns None."""
    entry = parse_hook_stdin("not json at all")
    assert entry is None


def test_log_write(tmp_path):
    """log_write appends a JSONL line to audit log."""
    log_file = tmp_path / "_audit_log.jsonl"
    entry = AuditEntry(
        session_id="sess-123",
        cwd="/project",
        tool_name="Edit",
        file_path="/project/src/main.py",
        state="EXECUTE",
    )
    log_write(entry, log_file)
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["session_id"] == "sess-123"
    assert record["file_path"] == "/project/src/main.py"
    assert record["state"] == "EXECUTE"
    assert "timestamp" in record


def test_log_write_appends(tmp_path):
    """Multiple log_write calls append, not overwrite."""
    log_file = tmp_path / "_audit_log.jsonl"
    for i in range(3):
        entry = AuditEntry(
            session_id=f"sess-{i}",
            cwd="/project",
            tool_name="Edit",
            file_path=f"/project/file{i}.py",
            state="EXECUTE",
        )
        log_write(entry, log_file)
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) == 3


def test_log_write_cross_project(tmp_path):
    """Cross-project write is flagged in log."""
    log_file = tmp_path / "_audit_log.jsonl"
    entry = AuditEntry(
        session_id="sess-123",
        cwd="/project_a",
        tool_name="Edit",
        file_path="/project_b/src/other.py",
        state="EXECUTE",
    )
    log_write(entry, log_file)
    record = json.loads(log_file.read_text().strip())
    assert record["cross_project"] is True


def test_read_audit_log(tmp_path):
    """read_audit_log returns list of dicts."""
    log_file = tmp_path / "_audit_log.jsonl"
    entry = AuditEntry(
        session_id="sess-1",
        cwd="/project",
        tool_name="Edit",
        file_path="/project/f.py",
        state="EXECUTE",
    )
    log_write(entry, log_file)
    records = read_audit_log(log_file)
    assert len(records) == 1
    assert records[0]["session_id"] == "sess-1"


def test_read_audit_log_missing(tmp_path):
    """Missing log file returns empty list."""
    log_file = tmp_path / "_audit_log.jsonl"
    records = read_audit_log(log_file)
    assert records == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_audit.py -v`
Expected: ImportError — no module `devlead.audit`

- [ ] **Step 3: Implement audit.py**

```python
# src/devlead/audit.py
"""Audit layer — log every file write with session context.

Parses Claude Code hook stdin JSON, extracts file_path + metadata,
appends to _audit_log.jsonl in claude_docs/.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class AuditEntry:
    """A single audit log entry."""

    session_id: str = ""
    cwd: str = ""
    tool_name: str = ""
    file_path: str | None = None
    state: str = ""
    agent_id: str | None = None
    agent_type: str | None = None


def parse_hook_stdin(stdin_text: str) -> AuditEntry | None:
    """Parse Claude Code hook stdin JSON into an AuditEntry.

    Returns None if JSON is malformed.
    """
    try:
        data = json.loads(stdin_text)
    except (json.JSONDecodeError, TypeError):
        return None

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path")

    return AuditEntry(
        session_id=data.get("session_id", ""),
        cwd=data.get("cwd", ""),
        tool_name=data.get("tool_name", ""),
        file_path=file_path,
        agent_id=data.get("agent_id"),
        agent_type=data.get("agent_type"),
    )


def log_write(entry: AuditEntry, log_file: Path) -> None:
    """Append an audit entry to the JSONL log file.

    Adds timestamp and cross_project flag automatically.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Detect cross-project write
    cross_project = False
    if entry.file_path and entry.cwd:
        try:
            file_resolved = str(Path(entry.file_path).resolve())
            cwd_resolved = str(Path(entry.cwd).resolve())
            cross_project = not file_resolved.startswith(cwd_resolved)
        except (ValueError, OSError):
            cross_project = False

    record = {
        "timestamp": now,
        "session_id": entry.session_id,
        "cwd": entry.cwd,
        "tool_name": entry.tool_name,
        "file_path": entry.file_path,
        "state": entry.state,
        "agent_id": entry.agent_id,
        "agent_type": entry.agent_type,
        "cross_project": cross_project,
    }

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a") as f:
        f.write(json.dumps(record) + "\n")


def read_audit_log(log_file: Path) -> list[dict]:
    """Read all entries from the audit log."""
    if not log_file.exists():
        return []
    entries = []
    for line in log_file.read_text().strip().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_audit.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/devlead/audit.py tests/test_audit.py
git commit -m "feat: audit.py — hook stdin parsing, write logging, cross-project detection"
```

---

## Task 2: Wire Audit Into Gate Check

**Files:**
- Modify: `src/devlead/state_machine.py`
- Modify: `src/devlead/cli.py`
- Test: `tests/test_audit_integration.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_audit_integration.py
"""Tests for audit integration with gate checks."""

import json
import pytest
from pathlib import Path
from devlead.state_machine import check_gate_with_audit, load_state, save_state, init_state
from devlead.audit import read_audit_log


def test_gate_logs_edit_to_audit(state_file, tmp_docs):
    """Gate check logs the file write to audit log."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-1",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "main.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 0

    records = read_audit_log(audit_log)
    assert len(records) == 1
    assert records[0]["state"] == "EXECUTE"
    assert "main.py" in records[0]["file_path"]


def test_gate_logs_blocked_write(state_file, tmp_docs):
    """Blocked writes are also logged (with state showing where it was blocked)."""
    state = init_state()
    state["state"] = "ORIENT"
    save_state(state, state_file)

    stdin_json = json.dumps({
        "session_id": "sess-2",
        "cwd": str(tmp_docs.parent),
        "tool_name": "Edit",
        "tool_input": {"file_path": str(tmp_docs.parent / "src" / "file.py")},
    })
    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", stdin_json, audit_log)
    assert exc.value.code == 2

    records = read_audit_log(audit_log)
    assert len(records) == 1
    assert records[0]["state"] == "ORIENT"


def test_gate_no_stdin_still_works(state_file, tmp_docs):
    """Gate works without stdin (backwards compat)."""
    state = init_state()
    state["state"] = "EXECUTE"
    save_state(state, state_file)

    audit_log = tmp_docs / "_audit_log.jsonl"
    with pytest.raises(SystemExit) as exc:
        check_gate_with_audit(state_file, "EXECUTE", "", audit_log)
    assert exc.value.code == 0
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_audit_integration.py -v`
Expected: ImportError — `check_gate_with_audit` not found

- [ ] **Step 3: Add check_gate_with_audit to state_machine.py**

Add to `src/devlead/state_machine.py` after `check_gate`:

```python
def check_gate_with_audit(
    state_file: Path,
    gate: str,
    stdin_text: str,
    audit_log: Path,
) -> None:
    """Gate check that also logs the write to the audit trail.

    Parses hook stdin for file_path context, logs before allow/block.
    Falls back to regular check_gate if stdin is empty.
    """
    from devlead.audit import parse_hook_stdin, log_write, AuditEntry

    # Parse stdin for audit context
    entry = parse_hook_stdin(stdin_text) if stdin_text else None

    # Load current state for audit
    current_state = ""
    if state_file.exists():
        state = load_state(state_file)
        current_state = state.get("state", "")

    # Log the write attempt (whether allowed or blocked)
    if entry and entry.file_path:
        entry.state = current_state
        log_write(entry, audit_log)

    # Delegate to existing gate logic
    check_gate(state_file, gate)
```

- [ ] **Step 4: Update cli.py gate command to read stdin and pass to audit**

Modify the gate handler in `src/devlead/cli.py`:

```python
    elif command == "gate":
        if len(args) < 2:
            print("Usage: devlead gate <EXECUTE|PLAN|SESSION_END>", file=sys.stderr)
            sys.exit(1)
        # Read hook stdin for audit context
        import sys as _sys
        stdin_text = ""
        if not _sys.stdin.isatty():
            stdin_text = _sys.stdin.read()
        audit_log = docs_dir / "_audit_log.jsonl"
        from devlead.state_machine import check_gate_with_audit
        check_gate_with_audit(state_file, args[1], stdin_text, audit_log)
```

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/test_audit_integration.py tests/test_audit.py -v`
Expected: all pass

- [ ] **Step 6: Run full test suite (ensure no regressions)**

Run: `python -m pytest tests/ -v`
Expected: all pass (existing gate tests still work since check_gate is unchanged)

- [ ] **Step 7: Commit**

```bash
git add src/devlead/state_machine.py src/devlead/cli.py tests/test_audit_integration.py
git commit -m "feat: wire audit logging into gate checks — log every file write"
```

---

## Task 3: Audit CLI — `devlead audit`

**Files:**
- Modify: `src/devlead/cli.py`
- Test: `tests/test_audit_cli.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_audit_cli.py
"""Tests for devlead audit CLI command."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "devlead"] + args,
        capture_output=True, text=True, cwd=str(cwd),
    )


def test_audit_show_empty(tmp_path):
    """devlead audit shows empty when no log."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    result = _run(["audit"], cwd=tmp_path)
    assert result.returncode == 0
    assert "No audit entries" in result.stdout


def test_audit_show_entries(tmp_path):
    """devlead audit shows logged entries."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    log = docs / "_audit_log.jsonl"
    log.write_text(json.dumps({
        "timestamp": "2026-04-05T10:00:00",
        "session_id": "sess-1",
        "cwd": str(tmp_path),
        "tool_name": "Edit",
        "file_path": str(tmp_path / "src" / "main.py"),
        "state": "EXECUTE",
        "cross_project": False,
    }) + "\n")
    result = _run(["audit"], cwd=tmp_path)
    assert result.returncode == 0
    assert "Edit" in result.stdout
    assert "main.py" in result.stdout


def test_audit_cross_project_flag(tmp_path):
    """devlead audit highlights cross-project writes."""
    docs = tmp_path / "claude_docs"
    docs.mkdir()
    log = docs / "_audit_log.jsonl"
    log.write_text(json.dumps({
        "timestamp": "2026-04-05T10:00:00",
        "session_id": "sess-1",
        "cwd": "/project_a",
        "tool_name": "Edit",
        "file_path": "/project_b/file.py",
        "state": "EXECUTE",
        "cross_project": True,
    }) + "\n")
    result = _run(["audit"], cwd=tmp_path)
    assert "CROSS" in result.stdout
```

- [ ] **Step 2: Implement audit CLI command**

Add to `COMMANDS` list in cli.py: `"audit"`

Add to USAGE help text: `  audit         Show file write audit log`

Add dispatch in main(): `elif command == "audit": _cmd_audit(docs_dir)`

Add handler:

```python
def _cmd_audit(docs_dir: Path) -> None:
    """Show audit log."""
    from devlead.audit import read_audit_log

    log_file = docs_dir / "_audit_log.jsonl"
    records = read_audit_log(log_file)

    if not records:
        print("No audit entries.")
        return

    for r in records:
        ts = r.get("timestamp", "?")[:19]
        tool = r.get("tool_name", "?")
        fp = r.get("file_path", "?")
        state = r.get("state", "?")
        cross = " [CROSS-PROJECT]" if r.get("cross_project") else ""
        agent = f" (agent: {r['agent_type']})" if r.get("agent_type") else ""
        print(f"  {ts} | {state:<10} | {tool:<6} | {fp}{cross}{agent}")
```

- [ ] **Step 3: Run tests**

Run: `python -m pytest tests/test_audit_cli.py -v`
Expected: 3 passed

- [ ] **Step 4: Commit**

```bash
git add src/devlead/cli.py tests/test_audit_cli.py
git commit -m "feat: devlead audit CLI — show file write audit log"
```

---

## Task 4: Configurable Audit Policy in devlead.toml

**Files:**
- Modify: `src/devlead/config.py`
- Test: `tests/test_config.py` (add tests)

- [ ] **Step 1: Write failing tests**

Add to `tests/test_config.py`:

```python
def test_default_audit_config():
    """Default config includes audit section."""
    assert "audit" in DEFAULT_CONFIG
    assert DEFAULT_CONFIG["audit"]["enabled"] is True
    assert DEFAULT_CONFIG["audit"]["cross_project_policy"] == "log"


def test_audit_config_from_toml(tmp_path):
    """Audit config loaded from toml."""
    toml = tmp_path / "devlead.toml"
    toml.write_text('[audit]\nenabled = true\ncross_project_policy = "warn"\n')
    config = load_config(tmp_path)
    assert config["audit"]["cross_project_policy"] == "warn"
```

- [ ] **Step 2: Add audit section to DEFAULT_CONFIG**

In `src/devlead/config.py`, add to `DEFAULT_CONFIG`:

```python
    "audit": {
        "enabled": True,
        "cross_project_policy": "log",  # "log", "warn", "block"
    },
```

- [ ] **Step 3: Update scaffold toml template**

Add to `src/devlead/scaffold/devlead_toml_template.toml`:

```toml
[audit]
enabled = true
cross_project_policy = "log"    # "log" = silent, "warn" = allow + warn, "block" = deny
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_config.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/devlead/config.py src/devlead/scaffold/devlead_toml_template.toml tests/test_config.py
git commit -m "feat: configurable audit policy in devlead.toml"
```

---

## Task 5: Strengthen Collab Pipeline — Message Types & Auto-Create

**Files:**
- Modify: `src/devlead/collab.py`
- Test: `tests/test_collab_pipeline.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_collab_pipeline.py -v`
Expected: ImportError

- [ ] **Step 3: Implement collab pipeline functions**

Add to `src/devlead/collab.py`:

```python
import shutil
from datetime import date


def _next_sequence(outbox: Path, prefix: str) -> int:
    """Find next sequence number for a given prefix in outbox."""
    existing = list(outbox.glob(f"{prefix}_*.md"))
    if not existing:
        return 1
    nums = []
    for f in existing:
        parts = f.stem.rsplit("_", 1)
        if parts[-1].isdigit():
            nums.append(int(parts[-1]))
    return max(nums, default=0) + 1


def _create_collab_message(
    project_dir: Path,
    msg_type: str,
    to_project: str,
    title: str,
    body: str,
    priority: str = "",
    blocks: str = "",
    references: str = "",
) -> Path:
    """Create a structured collab message in OUTBOX."""
    outbox = project_dir / ".collab" / "OUTBOX"
    outbox.mkdir(parents=True, exist_ok=True)

    prefix = f"{msg_type}_{to_project}"
    seq = _next_sequence(outbox, prefix)
    filename = f"{prefix}_{seq:03d}.md"
    filepath = outbox / filename

    today = str(date.today())
    from_project = project_dir.name

    lines = [
        f"# {msg_type}: {title}",
        "",
        f"> From: {from_project}",
        f"> To: {to_project}",
        f"> Date: {today}",
    ]
    if priority:
        lines.append(f"> Priority: {priority}")
    lines.append("> Status: OPEN")
    if blocks:
        lines.append(f"> Blocks: {blocks}")
    if references:
        lines.append(f"> References: {references}")
    lines.extend(["", "## Details", "", body, ""])

    filepath.write_text("\n".join(lines))
    return filepath


def create_change_request(project_dir, to_project, title, body, priority="", blocks=""):
    return _create_collab_message(project_dir, "CHANGE_REQUEST", to_project, title, body, priority=priority, blocks=blocks)


def create_issue_escalation(project_dir, to_project, title, body, priority=""):
    return _create_collab_message(project_dir, "ISSUE_ESCALATION", to_project, title, body, priority=priority)


def create_status_update(project_dir, to_project, title, body):
    return _create_collab_message(project_dir, "STATUS_UPDATE", to_project, title, body)


def create_feedback(project_dir, to_project, title, body, references=""):
    return _create_collab_message(project_dir, "FEEDBACK", to_project, title, body, references=references)


def sync_outbox_to_inbox(
    project_dir: Path, project_map: dict[str, Path]
) -> int:
    """Copy OUTBOX files to target project INBOXes.

    project_map: {project_name: project_path}
    Returns count of files synced.
    """
    outbox = project_dir / ".collab" / "OUTBOX"
    if not outbox.exists():
        return 0

    synced = 0
    for f in sorted(outbox.glob("*.md")):
        content = f.read_text()
        meta = parse_collab_file(content)
        target_name = meta.get("to", "")

        if target_name in project_map:
            target_inbox = project_map[target_name] / ".collab" / "INBOX"
            target_inbox.mkdir(parents=True, exist_ok=True)
            target_file = target_inbox / f.name
            if not target_file.exists():
                shutil.copy2(f, target_file)
                synced += 1

    return synced
```

Also update `parse_collab_file` regex to handle all message types:

```python
    # Replace the existing title regex line:
    m = re.match(r"^#\s+(REQUEST|FEEDBACK|CHANGE_REQUEST|ISSUE_ESCALATION|STATUS_UPDATE):\s*(.+)", line)
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_collab_pipeline.py tests/test_collab.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add src/devlead/collab.py tests/test_collab_pipeline.py
git commit -m "feat: collab pipeline — change requests, issue escalation, status updates, sync"
```

---

## Task 6: Wire Collab Sync Into CLI + Portfolio

**Files:**
- Modify: `src/devlead/cli.py`
- Modify: `src/devlead/collab.py` (minor — wire CLI subcommands)

- [ ] **Step 1: Add `collab sync` and expanded subcommands to cli.py**

Update `_cmd_collab` in `src/devlead/cli.py`:

```python
def _cmd_collab(sub_args: list[str]) -> None:
    """Cross-project collaboration."""
    from devlead.collab import (
        init_collab, scan_inbox, collab_status,
        create_change_request, create_issue_escalation,
        create_status_update, create_feedback,
        sync_outbox_to_inbox,
    )
    from devlead.portfolio import list_projects

    project_dir = Path.cwd()

    if not sub_args or sub_args[0] == "status":
        status = collab_status(project_dir)
        print(f"Collab: {status['inbox_count']} inbox | {status['outbox_count']} outbox | {status['open_requests']} open requests")
    elif sub_args[0] == "init":
        init_collab(project_dir)
        print("Collab channel initialized (.collab/INBOX/ and .collab/OUTBOX/).")
    elif sub_args[0] == "inbox":
        items = scan_inbox(project_dir)
        if not items:
            print("Inbox is empty.")
        else:
            for item in items:
                status_mark = "!!" if item.get("status", "").upper() == "OPEN" else "  "
                print(f"  {status_mark} {item['filename']} — {item.get('type', '?')}: {item.get('title', '?')} [{item.get('status', '?')}]")
    elif sub_args[0] == "sync":
        workspace = Path.home() / ".devlead"
        projects = list_projects(workspace)
        project_map = {p["name"]: Path(p["path"]) for p in projects}
        synced = sync_outbox_to_inbox(project_dir, project_map)
        print(f"Synced {synced} message(s) to target project inboxes.")
    else:
        print(f"Unknown collab subcommand: {sub_args[0]}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 2: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: all pass

- [ ] **Step 3: Commit**

```bash
git add src/devlead/cli.py
git commit -m "feat: devlead collab sync — push outbox to registered project inboxes"
```

---

## Task 7: Rollover Size-Based Trigger

**Files:**
- Modify: `src/devlead/rollover.py`
- Test: `tests/test_rollover_size.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_rollover_size.py
"""Tests for size-based rollover trigger."""

import shutil
from pathlib import Path
from datetime import date

import pytest

from devlead.rollover import should_rollover, do_rollover


FIXTURES = Path(__file__).parent / "fixtures"


def _setup_docs(tmp_path: Path) -> Path:
    docs = tmp_path / "claude_docs"
    docs.mkdir(exist_ok=True)
    for f in FIXTURES.glob("_*.md"):
        shutil.copy(f, docs / f.name)
    return docs


def test_should_rollover_date_trigger():
    """Date trigger fires on day_of_month."""
    assert should_rollover("date", day_of_month=5, today=date(2026, 4, 5)) is True
    assert should_rollover("date", day_of_month=1, today=date(2026, 4, 5)) is False


def test_should_rollover_size_trigger(tmp_path):
    """Size trigger fires when file exceeds max_lines."""
    docs = _setup_docs(tmp_path)
    tasks_file = docs / "_project_tasks.md"
    # Fixture has ~15 lines, test with low threshold
    assert should_rollover("size", max_lines=10, file_path=tasks_file) is True
    assert should_rollover("size", max_lines=100, file_path=tasks_file) is False


def test_should_rollover_size_missing_file(tmp_path):
    """Size trigger returns False for missing file."""
    assert should_rollover("size", max_lines=10, file_path=tmp_path / "nope.md") is False


def test_rollover_respects_size_trigger(tmp_path):
    """do_rollover with trigger='size' only rolls files exceeding max_lines."""
    docs = _setup_docs(tmp_path)

    # _project_tasks.md has ~15 lines, set threshold at 10
    do_rollover(
        docs,
        ["_project_tasks.md"],
        today=date(2026, 4, 5),
        trigger="size",
        max_lines=10,
    )
    assert (docs / "archive" / "_project_tasks_2026-04.md").exists()


def test_rollover_skips_small_files(tmp_path):
    """do_rollover with trigger='size' skips files under threshold."""
    docs = _setup_docs(tmp_path)

    do_rollover(
        docs,
        ["_project_tasks.md"],
        today=date(2026, 4, 5),
        trigger="size",
        max_lines=1000,
    )
    assert not (docs / "archive" / "_project_tasks_2026-04.md").exists()
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/test_rollover_size.py -v`
Expected: ImportError — `should_rollover` not found

- [ ] **Step 3: Implement should_rollover and update do_rollover**

Add to `src/devlead/rollover.py`:

```python
def should_rollover(
    trigger: str,
    day_of_month: int = 1,
    max_lines: int = 500,
    file_path: Path | None = None,
    today: date | None = None,
) -> bool:
    """Check if rollover should fire based on trigger type."""
    if today is None:
        today = date.today()

    if trigger == "date":
        return today.day == day_of_month
    elif trigger == "size":
        if file_path is None or not file_path.exists():
            return False
        line_count = len(file_path.read_text().splitlines())
        return line_count > max_lines

    return False
```

Update `do_rollover` signature to accept trigger params:

```python
def do_rollover(
    docs_dir: Path,
    files: list[str],
    today: date | None = None,
    trigger: str = "date",
    max_lines: int = 500,
) -> None:
```

Add at the top of the `for fname in files:` loop:

```python
        # Check trigger for size-based rollover
        if trigger == "size":
            if not should_rollover("size", max_lines=max_lines, file_path=source):
                continue
```

- [ ] **Step 4: Update cli.py rollover to pass trigger config**

Update `_cmd_rollover`:

```python
def _cmd_rollover(docs_dir: Path) -> None:
    """Run monthly rollover."""
    from devlead.config import load_config, get_rollover_config
    from devlead.rollover import do_rollover

    project_dir = docs_dir.parent
    config = load_config(project_dir)
    rollover_config = get_rollover_config(config)
    files = rollover_config.get("files", [])
    trigger = rollover_config.get("trigger", "date")
    max_lines = rollover_config.get("max_lines", 500)

    do_rollover(docs_dir, files, trigger=trigger, max_lines=max_lines)
    print(f"Rollover complete. {len(files)} files processed (trigger: {trigger}).")
```

- [ ] **Step 5: Run tests**

Run: `python -m pytest tests/test_rollover_size.py tests/test_rollover.py -v`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add src/devlead/rollover.py src/devlead/cli.py tests/test_rollover_size.py
git commit -m "feat: size-based rollover trigger — configurable date OR line count"
```

---

## Verification Checklist

After all tasks complete:

- [ ] `python -m pytest tests/ -v` — all tests pass
- [ ] `devlead audit` — shows audit log entries
- [ ] Gate check with stdin logs to `_audit_log.jsonl`
- [ ] Cross-project writes flagged in audit log
- [ ] `devlead collab sync` — pushes outbox to registered project inboxes
- [ ] All 4 collab message types create properly formatted files
- [ ] `devlead rollover` with `trigger = "size"` respects `max_lines`
- [ ] `devlead rollover` with `trigger = "date"` respects `day_of_month`
- [ ] `devlead.toml` `[audit]` section configures policy
- [ ] Zero external dependencies confirmed
