"""Cross-reference verifier for devlead_docs/. Implements FEATURES-0008.

Walks every cross-reference in devlead_docs/ and reports broken refs
(target missing) and orphans (pending intake entries older than 7 days).

Checks performed:
  - Intake entry `source` fields: scratchpad: prefix -> verify scratchpad
    entry exists; file paths -> verify file exists.
  - Scratchpad `> **Promoted:**` lines: extract intake ID, verify it exists
    in some `_intake_*.md`.
  - SOT block `receives_from` / `migrates_to`: verify referenced filenames
    exist in docs_dir.

ASCII only. Stdlib only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path

from devlead import audit, intake, scratchpad, sot

_PROMOTED_RE = re.compile(
    r">\s*\*\*Promoted:\*\*\s*([A-Z][A-Z0-9-]*-\d{4})", re.IGNORECASE
)

# SOT lineage values often carry parenthetical notes: "_scratchpad.md (via triage)"
# We extract just the filename portion before any space/paren.
_LINEAGE_FILE_RE = re.compile(r"^([^\s(]+\.md)")

_ORPHAN_DAYS = 7


@dataclass
class VerifyReport:
    """Result of verify_links()."""

    broken_refs: list[dict[str, str]] = field(default_factory=list)
    orphans: list[dict[str, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.broken_refs) == 0


def verify_links(docs_dir: Path) -> VerifyReport:
    """Walk every cross-reference in *docs_dir* and return a VerifyReport."""
    docs_dir = Path(docs_dir)
    report = VerifyReport()

    # --- Collect all known intake IDs across all intake files ---
    all_intake_ids: set[str] = set()
    intake_files = sorted(docs_dir.glob("_intake_*.md"))
    all_entries: list[tuple[intake.IntakeEntry, Path]] = []
    for f in intake_files:
        for entry in intake.read(f):
            all_intake_ids.add(entry.id)
            all_entries.append((entry, f))

    # --- Collect all known scratchpad entry IDs ---
    scratchpad_path = docs_dir / "_scratchpad.md"
    scratchpad_ids: set[str] = set()
    if scratchpad_path.exists():
        for entry_id, _title in scratchpad.iter_untriaged(scratchpad_path):
            scratchpad_ids.add(entry_id)

    # --- 1. Intake source field checks ---
    for entry, src_file in all_entries:
        source = entry.source.strip()
        if not source or source == "(pending)":
            continue
        if source.startswith("scratchpad:"):
            needle = source[len("scratchpad:"):]
            if needle and needle not in scratchpad_ids:
                report.broken_refs.append({
                    "source_file": src_file.name,
                    "field": f"{entry.id}.source",
                    "reference": source,
                    "reason": "scratchpad entry not found",
                })
        elif not source.startswith("http") and not source.startswith("#") and "#" not in source:
            # Treat as a file path (absolute or relative to docs_dir parent)
            ref_path = docs_dir.parent / source
            if not ref_path.exists():
                alt_path = docs_dir / source
                if not alt_path.exists():
                    report.broken_refs.append({
                        "source_file": src_file.name,
                        "field": f"{entry.id}.source",
                        "reference": source,
                        "reason": "referenced file not found",
                    })

    # --- 2. Scratchpad promoted-to lines ---
    if scratchpad_path.exists():
        text = scratchpad_path.read_text(encoding="utf-8")
        for m in _PROMOTED_RE.finditer(text):
            promoted_id = m.group(1).upper()
            if promoted_id not in all_intake_ids:
                report.broken_refs.append({
                    "source_file": "_scratchpad.md",
                    "field": "Promoted line",
                    "reference": promoted_id,
                    "reason": "intake ID not found in any _intake_*.md",
                })

    # --- 3. SOT lineage checks ---
    sot_blocks = sot.read_all(docs_dir)
    existing_md_files = {p.name for p in docs_dir.glob("*.md")}
    for filename, block in sot_blocks.items():
        for direction, refs in [
            ("receives_from", block.receives_from),
            ("migrates_to", block.migrates_to),
        ]:
            for ref_value in refs:
                fm = _LINEAGE_FILE_RE.match(ref_value)
                if not fm:
                    continue
                ref_file = fm.group(1)
                # Skip glob patterns (e.g. "_intake_*.md") — not literal filenames
                if "*" in ref_file or "?" in ref_file:
                    continue
                if ref_file not in existing_md_files:
                    report.broken_refs.append({
                        "source_file": filename,
                        "field": f"sot.lineage.{direction}",
                        "reference": ref_file,
                        "reason": "referenced file not found in docs_dir",
                    })

    # --- 4. Orphan detection (pending entries older than 7 days) ---
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=_ORPHAN_DAYS)
    for entry, src_file in all_entries:
        if entry.status != "pending":
            continue
        if not entry.captured:
            continue
        try:
            captured_dt = datetime.fromisoformat(
                entry.captured.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            continue
        if captured_dt < cutoff:
            age_days = (now - captured_dt).days
            report.orphans.append({
                "source_file": src_file.name,
                "entry_id": entry.id,
                "title": entry.title,
                "age_days": str(age_days),
                "reason": f"pending for {age_days} days (>{_ORPHAN_DAYS}d threshold)",
            })

    # --- Audit events ---
    if report.ok and not report.orphans:
        audit.append_event(docs_dir, "verify_pass", result="ok")
    else:
        audit.append_event(
            docs_dir,
            "verify_broken",
            result="broken",
            broken_count=len(report.broken_refs),
            orphan_count=len(report.orphans),
        )

    return report
