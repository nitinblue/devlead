---
description: "Append a raw capture entry to devlead_docs/_scratchpad.md - verbatim triage inbox, zero information loss."
---

You are running the `/devlead scratchpad <title>` command. Your job is to capture raw, untriaged notes from the current conversation into the project's scratchpad file.

## What the scratchpad is

`devlead_docs/_scratchpad.md` is DevLead's **raw capture inbox**. Anything the user has just said that doesn't yet have a dedicated home belongs here - verbatim or close to it - so nothing is lost while DevLead figures out where it belongs. It is permanent, read every session, and items flow OUT of it as they find proper homes. Triage is a separate command.

## What to do

1. **Think about what raw text needs capturing.** Look back at what the user has said in this conversation that has NOT yet been written into any `devlead_docs/` file. That's your candidate material. If `<title>` was provided on the command line, use it; otherwise pick a short descriptive title from the content.

2. **Read `devlead_docs/_scratchpad.md`** with the Read tool to see its current state and find the end of the existing entries.

3. **Append a new entry** using the Edit tool on `devlead_docs/_scratchpad.md`. The entry format is:

   ```
   ## Entry - YYYY-MM-DD - <title>

   <raw body>

   ---
   ```

   Use today's date. Place the new block after the last existing entry (or after the `## Entries` placeholder line if the file is empty of entries).

4. **Capture raw, not summarized.** Preserve the user's phrasing. Include full quotes where they exist. Include open questions, half-formed thoughts, lists, tables - whatever was actually said. Zero information loss is the rule. If you're tempted to compress, don't.

## What NOT to do

- Do not triage, reclassify, or move the entry into intake files, living docs, or the hierarchy. That is a separate step.
- Do not edit or delete existing scratchpad entries.
- Do not shell out to Python. This command is a direct Edit on the markdown file.
- Do not summarize away content to make the entry shorter. Length is fine; loss is not.

## Subcommand: `/devlead scratchpad archive`

Archives scratchpad entries that have already been promoted or migrated to intake files. An entry qualifies for archival when its body contains a `> **Promoted:**` or `> **Migrated:**` line AND the referenced intake entry is no longer `in_progress`.

Archived entries are moved to `devlead_docs/_scratchpad_archive.md` (append-only). Each archival writes a `scratchpad_archive` audit event. The source scratchpad entry is removed after successful archival.

Usage: `/devlead scratchpad archive [path-to-_scratchpad.md]`

## Report the result

Tell the user plainly: "Captured entry `<title>` into `devlead_docs/_scratchpad.md`." If nothing new was said this session that needed capturing, say so and do nothing.
