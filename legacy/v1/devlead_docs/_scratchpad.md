# Scratchpad

> Type: SCRATCHPAD
> Items here need triage. Run `devlead triage` to process.

## Active

| Key | Item | Source | Added | Status |
|-----|------|--------|-------|--------|
| SCRATCH-001 | Migration should be interactive Claude session, not silent script. DevLead scans, Claude presents findings to user, user classifies each existing file. Then guided TBO creation. Needs MIGRATE state in state machine or a special migrate flow. | model | 2026-04-05 | PENDING |
| SCRATCH-002 | Token tracking blocked: Claude Code hooks dont pass token_count in stdin. Two options: (1) request Anthropic add it to hook payload, (2) parse transcript_path JSONL if available. Check if transcript_path is passed in any hook type. | model | 2026-04-05 | PENDING |

## Archive

| Key | Item | Triaged To | Resolution |
|-----|------|------------|------------|
| SCRATCH-001 | Revenue timeline analysis -- need to cross-reference TBOs, distribution milestones, and gaps to give user a real answer about when product ships | ARCHIVED | TRIAGED |
| SCRATCH-003 | Pitch to Anthropic -- DevLead reduces wasted tokens and shadow work, puts control back to user. Could be official Claude Code plugin or recommended governance tool | ARCHIVED | TRIAGED |
| SCRATCH-004 | DevLead value prop for Anthropic: reduces frustration with LLM by enforcing articulation and prioritization before code | ARCHIVED | TRIAGED |
| SCRATCH-005 | Design the canonical project workbook format -- TBO→Story→Task in a single tabular view that becomes the standard report format across all DevLead commands | ARCHIVED | TRIAGED |
| SCRATCH-006 | Design the canonical project workbook format - TBO to Story to Task in a single tabular view that becomes the standard report format across all DevLead commands | ARCHIVED | TRIAGED |
| SCRATCH-007 | Intake tab clarification - items are raw requests (FEAT/BUG/GAP), not stories or tasks. Show status and priority. Once promoted to story, intake item gets CLOSED. | ARCHIVED | TRIAGED |
| SCRATCH-009 | Dashboard principle: no raw data dumps. Value-add aggregation, analysis, visual feedback only. | ARCHIVED | TRIAGED |
| SCRATCH-011 | Every dashboard tab needs a clear objective - what question does this tab answer for the user? | ARCHIVED | TRIAGED |
| SCRATCH-012 | Timeline Gantt should show milestone markers with dates on the bar - planned date marker and actual completion date marker, each labeled | ARCHIVED | TRIAGED |
| SCRATCH-015 | State machine update: INTAKE exit criteria should check scratchpad is empty (all items triaged). PLAN needs exit criteria: active task exists and links to a story. These are enforcement features, not guidelines. | ARCHIVED | TRIAGED |
| SCRATCH-016 | State machine redesign: guide with override, not strict enforcement. Show user recommended next step, let them skip/override. Record deviations in audit. Only hard blocks: no work without task, memory from docs only. Everything else is recommended flow with user choice. | ARCHIVED | TRIAGED |
| SCRATCH-017 | State machine: add TRIAGE state (accept/reject scratchpad items into intake) and PRIORITIZE state (rank accepted items, assign to phase/session, create tasks). TRIAGE = do we do this. PRIORITIZE = when do we do this. Flow: ORIENT -> TRIAGE -> PRIORITIZE -> PLAN -> EXECUTE -> UPDATE. | ARCHIVED | TRIAGED |
| SCRATCH-018 | Triage/Prioritize clarification: TRIAGE = accept (create ticket) or reject (archive). No priority at triage. PRIORITIZE = assign P1/P2/P3 to open tickets as standing attribute. Session scope = user picks subset for this session. DevLead recommends based on priority + TBO linkage + dependencies. | ARCHIVED | TRIAGED |
| SCRATCH-002 | Auto-publish HTML dashboard during session for visual feedback loop -- user shouldn't stare at terminal | FEAT-039 | TRIAGED |
| SCRATCH-008 | Audit tab - dont show .py files. Define clear objective for the tab. Should show governance enforcement actions, not raw file edits. | FEAT-040 | TRIAGED |
| SCRATCH-010 | KPIs tab is all wrong - need to review what KPIs make sense, which are broken, which should be removed | FEAT-041 | TRIAGED |
| SCRATCH-013 | Interactive server (devlead serve) - add to book of work, do not implement now. TASK-040 created but park it. | FEAT-042 | TRIAGED |
| SCRATCH-014 | DevLead feature: gate that blocks task creation unless scratchpad item has been triaged by user. Model captures in scratchpad, user triages and prioritizes, only then can a TASK be created. Prevents model from self-prioritizing. | FEAT-043 | TRIAGED |
| SCRATCH-019 | DevLead feature: auto-raise tickets for gaps/bugs observed in real-time during session. When DevLead detects an issue (e.g. gap command finds problems, audit detects deviation, state machine skip), it should create a ticket immediately in the right intake file. Not wait for model to remember. | FEAT-044 | TRIAGED |
| SCRATCH-020 | Session tab needs rethink - what question does it answer? Currently shows raw state transitions and checklists which are not meaningful to the user. Should show: what was accomplished this session tied to TBOs, how many tasks moved, time spent. | FEAT-045 | TRIAGED |{"item": "Token reporting - user wants this by hook or crook. Check if transcript_path is available in hook stdin, or find alternative approach to capture token usage per session/task.", "source": "user", "added": "2026-04-05"}
