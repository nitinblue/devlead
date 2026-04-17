"""Verify runner — runs every TTO verify: command and updates hierarchy checkboxes.

This is the mechanism that makes DevLead mark work as done, not Claude.
Reads verify: lines from _project_hierarchy.md, runs each command,
flips [ ] to [x] on pass, writes results to audit log.

Claude NEVER calls this to mark its own work done.
The Stop hook or `devlead verify-all` triggers it.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from devlead import audit


@dataclass
class VerifyResult:
    tto_id: str
    passed: bool
    output: str
    skipped: bool = False


def run_all(repo_root: Path) -> list[VerifyResult]:
    """Run every TTO verify command. Returns results."""
    repo_root = Path(repo_root).resolve()
    h_path = repo_root / "devlead_docs" / "_project_hierarchy.md"
    if not h_path.exists():
        return []

    text = h_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    results = []
    tto_id = None

    for line in lines:
        m = re.match(r"- \[[ xX]\] (TTO-\d+):", line)
        if m:
            tto_id = m.group(1)
            continue
        if tto_id and line.strip().startswith("verify:"):
            cmd = line.strip()[7:].strip()
            if cmd.startswith("echo "):
                results.append(VerifyResult(tto_id, False, cmd[5:].strip('"').strip("'")[:80], skipped=True))
            else:
                passed, output = _run_cmd(cmd, repo_root)
                results.append(VerifyResult(tto_id, passed, output))
                audit.append_event(
                    repo_root / "devlead_docs", "verify_tto",
                    tto_id=tto_id, result="pass" if passed else "fail",
                    output=output[:80],
                )
            tto_id = None

    return results


def update_hierarchy(repo_root: Path, results: list[VerifyResult]) -> list[str]:
    """Flip [ ] to [x] for passing TTOs in _project_hierarchy.md.

    Returns the list of TTO IDs that were newly flipped (i.e. transitioned
    from pending to done in this run). Caller can pass this to
    `promise_ledger.write_promises_for` to record what was promised.
    """
    h_path = repo_root / "devlead_docs" / "_project_hierarchy.md"
    if not h_path.exists():
        return []

    text = h_path.read_text(encoding="utf-8")
    flipped: list[str] = []
    passing_ids = {r.tto_id for r in results if r.passed and not r.skipped}

    for tto_id in passing_ids:
        pattern = f"- [ ] {tto_id}:"
        replacement = f"- [x] {tto_id}:"
        if pattern in text:
            text = text.replace(pattern, replacement, 1)
            flipped.append(tto_id)

    if flipped:
        h_path.write_text(text, encoding="utf-8")
    return flipped


def summary(results: list[VerifyResult]) -> str:
    passed = [r for r in results if r.passed and not r.skipped]
    failed = [r for r in results if not r.passed and not r.skipped]
    skipped = [r for r in results if r.skipped]
    lines = [f"VERIFIED: {len(passed)} pass, {len(failed)} fail, {len(skipped)} skip (not built)"]
    for r in passed:
        lines.append(f"  [PASS] {r.tto_id}")
    for r in failed:
        lines.append(f"  [FAIL] {r.tto_id}: {r.output}")
    for r in skipped:
        lines.append(f"  [SKIP] {r.tto_id}: {r.output}")
    return "\n".join(lines)


def _run_cmd(cmd: str, cwd: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15, cwd=str(cwd))
        output = (r.stdout.strip() or r.stderr.strip() or f"exit {r.returncode}")[:80]
        return r.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "timeout (15s)"
    except Exception as e:
        return False, str(e)[:80]
