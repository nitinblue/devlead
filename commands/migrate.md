---
description: Hash-checked, reversible content migration between devlead_docs/ files
---

# /devlead migrate

Usage:
  /devlead migrate <source-file> <section-heading> --to <dest-file>
  /devlead migrate rollback <migration-id>
  /devlead migrate list

## What this does

Moves a `## heading` section from one devlead_docs/ file to another with a
zero-loss guarantee. The destination file must already contain the section
content before removal from the source (copy-first pattern). A SHA-256 hash
of the stripped text is compared; if it doesn't match, the migration is
rejected with an error.

Every migration is logged to `devlead_docs/_migration_log.jsonl` and can be
rolled back by ID. Rollback re-inserts the section at its original position
in the source file.

## Subcommands

| Command | Description |
|---|---|
| `migrate <src> <heading> --to <dest>` | Extract section, verify hash in dest, remove from source |
| `migrate rollback <id>` | Re-insert section into source, mark log entry as rolled_back |
| `migrate list` | Print all migration records from the JSONL log |

## How Claude should run this

```
PYTHONPATH=src python -m devlead migrate devlead_docs/_scratchpad.md "Old entry" --to devlead_docs/_scratchpad_archive.md
PYTHONPATH=src python -m devlead migrate rollback abc123def456
PYTHONPATH=src python -m devlead migrate list
```

## Design decisions

- **Always strict.** Information loss is unrecoverable. There is no warn-only
  mode for migration -- if the hash doesn't match, the operation fails.
- **Copy-first pattern.** The caller must ensure the content exists in the
  destination before calling migrate. This prevents any window where content
  exists in neither file.
- **Append-only log.** `_migration_log.jsonl` is append-only. Rollback marks
  the entry as `rolled_back` but never deletes it.
- **Audit integration.** Every migrate and rollback writes an event to
  `_audit_log.jsonl` via `audit.append_event()`.
