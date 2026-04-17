"""Command-line dispatch for DevLead.

Routes `devlead <subcommand>` to the right module. Deliberately minimal - this is the
wrapper that slash commands invoke.
"""

from __future__ import annotations

import sys
from pathlib import Path


USAGE = """\
DevLead v2 (under construction)

Usage:
  devlead <command> [args]

Commands:
  init [path]                         Create devlead_docs/ in the current project
  scratchpad [path]                   List raw capture entries in _scratchpad.md
  scratchpad archive [path]            Archive promoted/migrated scratchpad entries
  intake [path-or-docs-dir]           List entries in _intake_*.md files
  triage                              Print current scratchpad entries (Claude-driven)
  ingest <plan> --into <file> [--forced]
                                      Ingest an external plugin plan into an intake file
  promote <needle> --into <file> | --to decision | --to fact --into <file> [--forced]
                                      Promote a scratchpad entry to intake / decision / fact
  focus [<entity-id> | show | clear]  Set, show, or clear the current focus entity
  awareness                           Refresh self-awareness files (_aware_*.md)
  gate <HookName>                     Run the enforcement gate (reads hook JSON from stdin)
  migrate <src> <heading> --to <dest>  Hash-checked section migration between files
  migrate rollback <id>               Roll back a migration by ID
  migrate list                        List all recorded migrations
  audit recent [N]                    Print the last N events from _audit_log.jsonl
  verify-links                        Walk cross-references and report broken refs + orphans
  dashboard                           Generate project management dashboard (HTML)
  config show                         Pretty-print the resolved devlead.toml + defaults
  --version                           Show version and exit

The bridge/intake flow is documented in docs/plugin-bridge.md.
Other commands ship in Week 2+ (see devlead_docs/_resume.md).
"""


def main(argv: list[str] | None = None) -> int:
    from devlead import __version__

    args = list(argv if argv is not None else sys.argv[1:])

    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return 0

    if args[0] in ("-V", "--version", "version"):
        print(f"devlead {__version__}")
        return 0

    cmd = args[0]

    if cmd == "init":
        return _cmd_init(args[1:])
    if cmd == "scratchpad":
        return _cmd_scratchpad(args[1:])
    if cmd == "intake":
        return _cmd_intake(args[1:])
    if cmd == "triage":
        return _cmd_triage(args[1:])
    if cmd == "ingest":
        return _cmd_ingest(args[1:])
    if cmd == "promote":
        return _cmd_promote(args[1:])
    if cmd == "focus":
        return _cmd_focus(args[1:])
    if cmd == "awareness":
        return _cmd_awareness(args[1:])
    if cmd == "gate":
        return _cmd_gate(args[1:])
    if cmd == "audit":
        return _cmd_audit(args[1:])
    if cmd == "migrate":
        return _cmd_migrate(args[1:])
    if cmd == "verify-links":
        return _cmd_verify_links(args[1:])
    if cmd == "dashboard":
        from devlead import dashboard
        out = dashboard.write_dashboard(Path(args[1]) if len(args) > 1 else Path.cwd())
        print(f"Dashboard: {out}")
        return 0
    if cmd == "config":
        return _cmd_config(args[1:])
    if cmd == "verify-all":
        from devlead import hierarchy, promise_ledger, resume, verifier
        repo = Path.cwd()
        results = verifier.run_all(repo)
        flipped = verifier.update_hierarchy(repo, results)
        print(verifier.summary(results))
        if flipped:
            print(f"\n{len(flipped)} TTOs checked in _project_hierarchy.md")
            # Write a promise-ledger row for every TTO that just transitioned
            # to done. Skips TTOs without an intent_vector (infrastructural).
            sprints = hierarchy.parse(repo / "devlead_docs" / "_project_hierarchy.md")
            written = promise_ledger.write_promises_for(
                repo / "devlead_docs" / promise_ledger.LEDGER_FILENAME,
                sprints, flipped,
            )
            if written:
                print(f"{len(written)} promise-ledger rows written")
            resume.refresh(repo)
            print("_resume.md regenerated")
        return 0
    if cmd == "report":
        return _cmd_report(args[1:])
    if cmd == "resume":
        return _cmd_resume(args[1:])
    if cmd == "kpi":
        return _cmd_kpi(args[1:])
    if cmd == "metric-update":
        return _cmd_metric_update(args[1:])
    if cmd == "realisation-sweep":
        return _cmd_realisation_sweep(args[1:])
    if cmd == "project-init":
        return _cmd_project_init(args[1:])
    if cmd == "render":
        return _cmd_render(args[1:])

    # Unknown command -> exit 0 (warn-only by design).
    print(f"devlead: unknown command '{cmd}' (v2 under construction)", file=sys.stderr)
    return 0


def _cmd_init(sub_args: list[str]) -> int:
    from devlead.install import install

    target = Path(sub_args[0]) if sub_args else Path.cwd()
    report = install(target)
    print(report.summary())
    return 0 if report.ok else 1


def _cmd_scratchpad(sub_args: list[str]) -> int:
    from devlead import scratchpad

    # Sub-subcommand: scratchpad archive [path]
    if sub_args and sub_args[0] == "archive":
        archive_args = sub_args[1:]
        path = Path(archive_args[0]) if archive_args else Path("devlead_docs") / "_scratchpad.md"
        if not path.exists():
            print(f"not found: {path}")
            return 1
        count = scratchpad.archive_promoted(path)
        if count == 0:
            print("scratchpad archive: nothing to archive")
        else:
            print(f"scratchpad archive: archived {count} entries to _scratchpad_archive.md")
        return 0

    path = Path(sub_args[0]) if sub_args else Path("devlead_docs") / "_scratchpad.md"
    if not path.exists():
        print(f"not found: {path}")
        return 1
    entries = scratchpad.iter_untriaged(path)
    if not entries:
        print("(no entries)")
        return 0
    for entry_id, title in entries:
        print(f"{entry_id}\t{title}")
    return 0


def _cmd_intake(sub_args: list[str]) -> int:
    from devlead import intake

    docs_dir = Path("devlead_docs")
    single_file: Path | None = None
    if sub_args:
        arg = Path(sub_args[0])
        if arg.is_file():
            single_file = arg
        elif arg.is_dir():
            docs_dir = arg
        else:
            print(f"not found: {arg}")
            return 1

    if single_file is not None:
        _print_intake_file(single_file, intake)
        return 0

    files = sorted(docs_dir.glob("_intake_*.md"))
    if not files:
        print(f"(no _intake_*.md files in {docs_dir})")
        return 0
    for f in files:
        _print_intake_file(f, intake)
    return 0


def _print_intake_file(path: Path, intake_module) -> None:
    print(f"[{path.name}]")
    entries = intake_module.read(path)
    if not entries:
        print("  (no entries)")
        return
    for e in entries:
        print(f"  {e.id}  {e.status:<9}  {e.title}")


def _cmd_triage(sub_args: list[str]) -> int:
    # Triage is Claude-driven. The shell command just prints the scratchpad.
    print("Triage walks _scratchpad.md entries. Current entries:")
    return _cmd_scratchpad([])


def _cmd_ingest(sub_args: list[str]) -> int:
    from devlead import bridge

    into: str | None = None
    from_scratch: str | None = None
    forced = False
    positional: list[str] = []
    i = 0
    while i < len(sub_args):
        if sub_args[i] == "--into" and i + 1 < len(sub_args):
            into = sub_args[i + 1]
            i += 2
            continue
        if sub_args[i] == "--from-scratchpad" and i + 1 < len(sub_args):
            from_scratch = sub_args[i + 1]
            i += 2
            continue
        if sub_args[i] == "--forced":
            forced = True
            i += 1
            continue
        positional.append(sub_args[i])
        i += 1

    if not into:
        print("--into required (e.g. --into _intake_features.md)")
        return 1

    docs_dir = Path("devlead_docs")
    origin = "forced" if forced else "normal"

    try:
        if from_scratch:
            if positional:
                docs_dir = Path(positional[0])
            scratchpad_path = docs_dir / "_scratchpad.md"
            entry = bridge.ingest_from_scratchpad(
                scratchpad_path, from_scratch, into, docs_dir, origin=origin
            )
        else:
            if not positional:
                print("usage: devlead ingest <plan-path> --into <_intake_file.md> [--forced]")
                print("   or: devlead ingest --from-scratchpad <needle> --into <_intake_file.md> [--forced]")
                return 1
            plan_path = Path(positional[0])
            if len(positional) > 1:
                docs_dir = Path(positional[1])
            entry = bridge.ingest(plan_path, into, docs_dir, origin=origin)
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}")
        return 1

    print(f"wrote {entry.id}: {entry.title}")
    print(f"  into: {into}")
    print(f"  source: {entry.source}")
    print(f"  origin: {entry.origin}")
    print(f"  actionable items: {len(entry.actionable_items)}")
    return 0


def _cmd_awareness(sub_args: list[str]) -> int:
    from devlead import awareness

    repo_root = Path(sub_args[0]) if sub_args else Path.cwd()
    docs_dir = repo_root / "devlead_docs"
    if not docs_dir.exists():
        print(f"error: {docs_dir} not found; run `devlead init` first")
        return 1
    features_path, design_path = awareness.refresh(repo_root, docs_dir)
    from devlead import audit
    audit.append_event(docs_dir, "awareness_refresh", result="ok")
    print(f"refreshed: {features_path.relative_to(repo_root)}")
    print(f"refreshed: {design_path.relative_to(repo_root)}")
    return 0


def _cmd_focus(sub_args: list[str]) -> int:
    from devlead import intake

    docs_dir = Path("devlead_docs")
    if not docs_dir.exists():
        print(f"error: {docs_dir} not found; run `devlead init` first")
        return 1

    if not sub_args or sub_args[0] == "show":
        in_progress = intake.list_by_status(docs_dir, "in_progress")
        if not in_progress:
            print("focus: (none)")
            return 0
        print(f"focus ({len(in_progress)} in_progress):")
        for entry, path in in_progress:
            print(f"  {entry.id}  {entry.title}  [{path.name}]")
        return 0

    if sub_args[0] == "clear":
        in_progress = intake.list_by_status(docs_dir, "in_progress")
        count = 0
        for entry, path in in_progress:
            if intake.update_status(path, entry.id, "pending"):
                count += 1
        print(f"focus: cleared {count} entries back to pending")
        return 0

    entity_id = sub_args[0]
    found = intake.find_entry(docs_dir, entity_id)
    if found is None:
        print(f"error: entity {entity_id} not found in any _intake_*.md file")
        return 1
    entry, path = found
    intake.update_status(path, entity_id, "in_progress")
    from devlead import audit
    audit.append_event(docs_dir, "focus_change", intake_id=entity_id, result="in_progress")
    print(f"focus: {entity_id} -> in_progress [{path.name}]")
    return 0


def _cmd_promote(sub_args: list[str]) -> int:
    from devlead import bridge

    needle: str | None = None
    target: str = "intake"
    into: str | None = None
    forced = False

    i = 0
    while i < len(sub_args):
        arg = sub_args[i]
        if arg == "--to" and i + 1 < len(sub_args):
            target = sub_args[i + 1]
            i += 2
            continue
        if arg == "--into" and i + 1 < len(sub_args):
            into = sub_args[i + 1]
            i += 2
            continue
        if arg == "--forced":
            forced = True
            i += 1
            continue
        if needle is None:
            needle = arg
        i += 1

    if not needle:
        print("usage: devlead promote <needle> --into <_intake_*.md>")
        print("   or: devlead promote <needle> --to decision")
        print("   or: devlead promote <needle> --to fact --into <_living_*.md>")
        return 1

    docs_dir = Path("devlead_docs")
    scratchpad_path = docs_dir / "_scratchpad.md"
    origin = "forced" if forced else "normal"

    try:
        if target == "intake":
            if not into:
                print("--into required when --to intake (e.g. --into _intake_features.md)")
                return 1
            entry = bridge.ingest_from_scratchpad(
                scratchpad_path, needle, into, docs_dir, origin=origin
            )
            print(f"promoted to intake: {entry.id}: {entry.title}")
            print(f"  into: {into}")
            print(f"  source: {entry.source}")
            print(f"  origin: {entry.origin}")
            print(f"  actionable items: {len(entry.actionable_items)}")
            return 0
        if target == "decision":
            result = bridge.promote_to_living(
                scratchpad_path, needle, "_living_decisions.md", docs_dir
            )
            print(f"promoted to decision: {result}")
            return 0
        if target == "fact":
            if not into:
                print("--into required when --to fact (e.g. --into _living_glossary.md)")
                return 1
            result = bridge.promote_to_living(
                scratchpad_path, needle, into, docs_dir
            )
            print(f"promoted to fact: {result}")
            return 0
        print(f"unknown --to: {target} (use intake|decision|fact)")
        return 1
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}")
        return 1




def _cmd_migrate(sub_args: list[str]) -> int:
    from devlead import migrate as mig

    docs_dir = Path("devlead_docs")

    if not sub_args:
        print("usage: devlead migrate <source-file> <section-heading> --to <dest-file>")
        print("       devlead migrate rollback <migration-id>")
        print("       devlead migrate list")
        return 0

    # Sub-subcommands
    if sub_args[0] == "rollback":
        if len(sub_args) < 2:
            print("usage: devlead migrate rollback <migration-id>")
            return 1
        try:
            msg = mig.rollback(sub_args[1], docs_dir)
            print(msg)
            return 0
        except ValueError as e:
            print(f"error: {e}")
            return 1

    if sub_args[0] == "list":
        records = mig.list_migrations(docs_dir)
        if not records:
            print("(no migrations)")
            return 0
        print(f"{'ID':<14} {'STATUS':<13} {'SECTION':<30} {'SOURCE'}")
        for r in records:
            print(f"{r.id:<14} {r.status:<13} {r.section_heading:<30} {r.source}")
        return 0

    # migrate <source> <heading> --to <dest>
    to_file: str | None = None
    positional: list[str] = []
    i = 0
    while i < len(sub_args):
        if sub_args[i] == "--to" and i + 1 < len(sub_args):
            to_file = sub_args[i + 1]
            i += 2
            continue
        positional.append(sub_args[i])
        i += 1

    if len(positional) < 2 or not to_file:
        print("usage: devlead migrate <source-file> <section-heading> --to <dest-file>")
        return 1

    source_path = Path(positional[0])
    heading = positional[1]
    dest_path = Path(to_file)

    try:
        record = mig.migrate(source_path, heading, dest_path, docs_dir)
        print(f"migrated: {record.id}")
        print(f"  section: ## {record.section_heading}")
        print(f"  from: {record.source}")
        print(f"  to:   {record.dest}")
        print(f"  hash: {record.content_hash[:16]}..")
        return 0
    except ValueError as e:
        print(f"error: {e}")
        return 1


def _cmd_gate(sub_args: list[str]) -> int:
    """Run the enforcement gate. Reads JSON from stdin, prints JSON to stdout.

    Always returns exit 0 (warn-only by design - locked decision).
    """
    import json
    from devlead import gate

    hook_name = sub_args[0] if sub_args else "PreToolUse"
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, OSError):
        payload = {}

    result = gate.check(hook_name, payload, Path.cwd())
    print(json.dumps(result, ensure_ascii=True))
    return 0


def _cmd_audit(sub_args: list[str]) -> int:
    from devlead import audit

    docs_dir = Path("devlead_docs")
    if not sub_args or sub_args[0] != "recent":
        print("usage: devlead audit recent [N]")
        return 0
    n = 20
    if len(sub_args) > 1:
        try:
            n = int(sub_args[1])
        except ValueError:
            print(f"audit: invalid N: {sub_args[1]}")
            return 0
    events = audit.tail(docs_dir, n)
    if not events:
        print("(no audit events)")
        return 0
    import json
    for ev in events:
        print(json.dumps(ev, ensure_ascii=True))
    return 0


def _cmd_verify_links(sub_args: list[str]) -> int:
    from devlead import verify

    docs_dir = Path(sub_args[0]) if sub_args else Path("devlead_docs")
    if not docs_dir.exists():
        print(f"error: {docs_dir} not found; run `devlead init` first")
        return 1

    report = verify.verify_links(docs_dir)

    if report.broken_refs:
        print(f"Broken refs ({len(report.broken_refs)}):")
        for ref in report.broken_refs:
            print(f"  [{ref['source_file']}] {ref['field']} -> {ref['reference']}")
            print(f"    reason: {ref['reason']}")
    if report.orphans:
        print(f"Orphans ({len(report.orphans)}):")
        for orph in report.orphans:
            print(f"  [{orph['source_file']}] {orph['entry_id']} - {orph['title']}")
            print(f"    {orph['reason']}")
    if report.ok and not report.orphans:
        print("verify-links: all references valid, no orphans.")
    return 0 if report.ok else 1


def _cmd_dashboard(sub_args: list[str]) -> int:
    from devlead import dashboard

    repo_root = Path(sub_args[0]) if sub_args else Path.cwd()
    out_path = dashboard.write_dashboard(repo_root)
    print(f"Dashboard written to: {out_path}")
    return 0


def _cmd_config(sub_args: list[str]) -> int:
    from devlead import config

    if not sub_args or sub_args[0] != "show":
        print("usage: devlead config show")
        return 0
    cfg = config.load(Path.cwd())
    cfg_path = cfg.repo_root / "devlead.toml"
    print(f"# devlead config (repo_root={cfg.repo_root})")
    print(f"# source: {'devlead.toml + defaults' if cfg_path.exists() else 'defaults only (no devlead.toml)'}")
    for section_name in ("memory", "enforcement", "audit", "intake"):
        section = cfg.section(section_name)
        if not section:
            continue
        print()
        print(f"[{section_name}]")
        for k, v in section.items():
            if isinstance(v, list):
                items = ", ".join(repr(x) for x in v)
                print(f"  {k} = [{items}]")
            elif isinstance(v, str):
                print(f"  {k} = {v!r}")
            else:
                print(f"  {k} = {v}")
    return 0

def _cmd_kpi(sub_args: list[str]) -> int:
    from devlead import kpi

    repo_root = Path(sub_args[0]) if sub_args else Path.cwd()
    results = kpi.compute(repo_root)
    print(kpi.summary(results))
    return 0


def _cmd_resume(sub_args: list[str]) -> int:
    from devlead import resume

    repo_root = Path(sub_args[0]) if sub_args else Path.cwd()
    out = resume.refresh(repo_root)
    print(f"_resume.md regenerated from project state: {out}")
    return 0


def _cmd_report(sub_args: list[str]) -> int:
    from devlead import report

    repo_root = Path(sub_args[0]) if sub_args else Path.cwd()
    out_path = report.write_report(repo_root)
    print(f"Report written to: {out_path}")
    return 0


def _cmd_render(sub_args: list[str]) -> int:
    """`devlead render` — produce HTML views of every devlead_docs/*.md.

    FEATURES-0024 (foundation of MD↔HTML loop). Reads every Markdown file in
    devlead_docs/ and writes a rendered HTML file to docs/views/ alongside
    an index.html linking them. Read-only views in v1; edit-back daemon is
    FEATURES-0029.
    """
    from devlead import render

    repo = Path.cwd()
    docs_dir = repo / "devlead_docs"
    out_dir = repo / "docs" / render.VIEWS_DIRNAME
    rendered = render.render_dir(docs_dir, out_dir)
    print(f"rendered {len(rendered)} files to {out_dir}")
    print(f"index: {out_dir / 'index.html'}")
    return 0


def _cmd_project_init(sub_args: list[str]) -> int:
    """`devlead project-init [lock|generate-intake]`

    No subcommand: runs the interactive 10-question interview, writes answers
    to devlead_docs/_project_init_answers.md.

    `lock`: hashes _project_hierarchy.md and appends a lock entry to
    _living_decisions.md (idempotent on same hash).

    `generate-intake`: emits hierarchy-derived intake files
    (_intake_hierarchy_features.md and _intake_hierarchy_nonfunctional.md)
    by walking the parsed hierarchy and splitting TTOs by ttype.
    """
    from devlead import hierarchy, project_init

    repo = Path.cwd()
    docs_dir = repo / "devlead_docs"
    sub = sub_args[0] if sub_args else ""

    if sub == "lock":
        h_path = docs_dir / "_project_hierarchy.md"
        d_path = docs_dir / "_living_decisions.md"
        if not h_path.exists():
            print("no _project_hierarchy.md to lock", file=sys.stderr)
            return 1
        h = project_init.lock_hierarchy(h_path, d_path)
        print(f"hierarchy hash: {h}")
        return 0

    if sub == "generate-intake":
        h_path = docs_dir / "_project_hierarchy.md"
        if not h_path.exists():
            print("no _project_hierarchy.md to derive from", file=sys.stderr)
            return 1
        sprints = hierarchy.parse(h_path)
        counts = project_init.generate_intake_from_ttos(sprints, docs_dir)
        for fname, n in counts.items():
            print(f"{fname}: {n} entries")
        return 0

    # Default: run interview
    answers = project_init.interview()
    answers_path = docs_dir / project_init.ANSWERS_FILENAME
    project_init.write_answers(answers, answers_path)
    print(f"\nAnswers written to: {answers_path}")
    print("Next: paste the suggested prompt into Claude to draft the hierarchy,")
    print("      then run: devlead project-init lock")
    return 0


def _cmd_realisation_sweep(sub_args: list[str]) -> int:
    """`devlead realisation-sweep`

    Walks _promise_ledger.jsonl, finds rows whose window has expired, and
    computes φ/ε from current BO metrics. Updates row status to
    realised | partial | vapor (skips when no data is available).
    """
    from devlead import hierarchy, metric_source, promise_ledger

    repo = Path.cwd()
    docs_dir = repo / "devlead_docs"
    h_path = docs_dir / "_project_hierarchy.md"
    if not h_path.exists():
        print("no _project_hierarchy.md", file=sys.stderr)
        return 1

    sprints = hierarchy.parse(h_path)
    metric_source.apply_to_sprints(docs_dir / metric_source.HISTORY_FILENAME, sprints)
    result = promise_ledger.run_realisation_sweep(
        docs_dir / promise_ledger.LEDGER_FILENAME, sprints,
    )
    print(
        f"realisation sweep: checked {result['checked']} "
        f"window-expired rows, updated {result['updated']} "
        f"(skipped {result['skipped_no_data']} for missing data)"
    )
    return 0


def _cmd_metric_update(sub_args: list[str]) -> int:
    """`devlead metric-update <BO-ID> <value> [--note "..."]`

    Records a manual metric reading into devlead_docs/_state_history.jsonl.
    Used by the manual mode of metric_source — for shell/url modes, the Stop
    hook will write the same row automatically (deferred).
    """
    from devlead import metric_source

    if len(sub_args) < 2:
        print(
            "usage: devlead metric-update <BO-ID> <value> [--note '...']",
            file=sys.stderr,
        )
        return 1
    bo_id, value_str = sub_args[0], sub_args[1]
    note = ""
    if "--note" in sub_args:
        i = sub_args.index("--note")
        if i + 1 < len(sub_args):
            note = sub_args[i + 1]
    try:
        value = float(value_str)
    except ValueError:
        print(f"value '{value_str}' is not a number", file=sys.stderr)
        return 1
    history_path = Path.cwd() / "devlead_docs" / metric_source.HISTORY_FILENAME
    row = metric_source.record_reading(history_path, bo_id, value, note=note)
    print(f"recorded: {bo_id} = {row['value']} at {row['ts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
