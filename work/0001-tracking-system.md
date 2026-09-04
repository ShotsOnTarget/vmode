# Intent 0001: work tracking system

Bootstrap note: the work record does not exist yet, so this Intent lives as a file. It moves into the record as the first item once Story 0001-1 is done.

- **Id**: 0001
- **What we want**: one system that records every work item per policy section 4, with a simple screen for the Board and a way for agents to read and write it directly.
- **Why**: without it nothing is traceable and the Supervisor has nothing to run against.
- **Care level**: High. Every later piece depends on it.
- **How the Board will say yes**: shown an Intent walked forward to code and a line of code walked back to its Intent, on the Board screen, without anyone explaining.
- **Out of scope**: the Supervisor itself, the size and shape checker, any product code.

## Architect decision: technology

Backend: **beads**. Reasons against the policy section 4 list.

| Policy needs | beads has | Gap |
|---|---|---|
| Unique permanent id | Hierarchical ids, never reused | None |
| Kind, parent, links | Labels; dependency types parent-child, blocks, validates | None. beads 1.0 has a native `validates` link, which is "checks". The label convention accepted as decision 2 is not needed. |
| One owner | Assignee | None |
| Fixed states | open, in_progress, blocked, closed; "ready" is computed from blockers | "checking" and "reopened" become labels |
| Append-only history | beads 1.0 stores in embedded Dolt: every change is a versioned commit, readable with `--as-of`. JSONL export committed to git. | None. The Supervisor log stays a separate file so it is readable without the tool. |
| Trace both ways | Dependency graph, `bd ready`, tree views | Orphan check is a small script, not built in |
| Agents read directly | CLI with JSON output, MCP server | None. CLI is the harness-neutral path. |

Not chosen: a hosted tracker (agents need auth and network, audit trail is theirs not ours), a hand-rolled SQLite app (rebuilds what beads already has).

Frontend: **adopt an existing beads web UI before building one.** Candidates: beads-dashboard, beads-web. Story 0001-3 evaluates them against the four things the Board actually does. Build our own only if both fail, and then only those four things.

Agent access: one skill, `work-record`, that wraps the CLI. Every role skill points at it instead of naming the tool.

## Board decisions

1. Record lives inside this git repo: **accepted** 2026-09-04.
2. "Checks" link as child plus label convention: **accepted** 2026-09-04, then found unnecessary: beads 1.0 has a native `validates` link. Using that instead. No Board action needed.
3. Third-party Board screen: **accepted** 2026-09-04.

## System shape

Four parts. Arrows are data flow.

```
Board screen  <---- reads ----  record (beads, in git)  <---- reads/writes ----  work-record skill  <---- Architect, Builders
      |                              ^                                                    ^
      +---- records yes/no ----------+                                                    |
                                                                                          |
Supervisor (code, later)  ---- reads record, writes log ---->  log (append-only file)      |
                                       \--------------------- hands jobs to ------------+
```

## Stories

### Story 0001-1: the record exists and holds the six kinds

- **Parent Intent**: 0001
- **One thing it must do**: a fresh checkout can create, link, list and update all six item kinds with owner and state.
- **Customer**: the work-record skill (0001-4) and the trace tools (0001-2). Later, the Supervisor.
- **Supplier**: beads, adopted as is, plus a thin set of wrapper functions written by Builders.
- **Inputs**: a command with item kind, title, parent id, owner, and optional links, from a caller on the command line.
- **Outputs**: the created or updated item as a JSON object, and the record file in git updated.
- **Contract**:
  - Ids are permanent and never reused.
  - Kind is one of exactly six values: intent, story, code, test, verification, validation. Any other value is rejected.
  - Every item except an intent has exactly one parent. Create without a parent is rejected for the other five kinds.
  - Every item has exactly one owner. Create without an owner is rejected.
  - State is one of: waiting, ready, in_progress, blocked, checking, done, reopened. Anything else is rejected.
  - Link is one of: parent_of, needs_first, checks. Anything else is rejected.
  - Every write lands in the git-tracked record file before the command returns.
  - Output is always JSON on stdout, errors always JSON on stderr with a non-zero exit.
- **Checklist**:
  1. `init` in a clean folder produces a record with no items. [testing]
  2. Each of the six kinds can be created with the kind label, and listed back filtered by kind. [testing]
  3. Creating a non-intent without a parent is rejected. [testing]
  4. Creating any item without an owner is rejected. [testing]
  5. Each of the three link types can be added and read back; a fourth is rejected. [testing]
  6. Each of the seven states can be set and read back; an eighth is rejected. [testing]
  7. A convention document maps each policy field to a beads field, label, or convention. [looking]
- **Job pairs**: `record_run`, `record_init`, `record_create_item`, `record_add_link`, `record_set_state`, `record_list_kind`
- **Needs first**: none

### Story 0001-2: trace both ways and find orphans

- **Parent Intent**: 0001
- **One thing it must do**: given any id, walk up to its Intent and down to every leaf, and report every orphan in the record.
- **Customer**: the Supervisor, which runs the orphan check at every gate. The Board screen, which shows traces. The Architect, when verifying a Story.
- **Supplier**: Builders, writing three small functions over the record's JSON output.
- **Inputs**: the record, and for trace functions one item id.
- **Outputs**: trace back: an ordered list of items from the given id up to the intent. Trace forward: a tree rooted at the given id. Orphans: a list of items with the rule each one breaks.
- **Contract**:
  - Trace back on an intent returns just the intent.
  - Trace back never loops; a cycle in the record is reported as an error, not followed.
  - Trace forward includes every descendant by parent_of and every item linked by checks.
  - Orphan rules, exactly these three: non-intent with no parent; left item (intent, story, code) with no checks link pointing at it; right item (validation, verification, test) with no checks link pointing from it.
  - Zero orphans exits success. One or more exits non-zero with the list. The Supervisor relies on the exit code.
  - Output is JSON.
- **Checklist**:
  1. Trace back from a code job returns job, story, intent, in that order. [testing]
  2. Trace forward from an intent returns every story, pair, and check under it. [testing]
  3. A story with no verification is reported as an orphan. [testing]
  4. A test job with no checks link is reported as an orphan. [testing]
  5. A story with no parent is reported as an orphan. [testing]
  6. A cycle is reported as an error and does not hang. [testing]
  7. A clean record reports zero orphans and exits success. [testing]
- **Job pairs**: `trace_back`, `trace_forward`, `find_orphans`
- **Needs first**: 0001-1

### Story 0001-3: the Board screen

- **Parent Intent**: 0001
- **One thing it must do**: the Board can do its four jobs on a screen without a terminal.
- **Customer**: the Board.
- **Supplier**: Builders, after both existing UIs failed evaluation.
- **Inputs**: the record, read live. A yes or no decision typed by the Board.
- **Outputs**: on screen: intent list with rollup, forward tree, back trace. Into the record: the Board's decision as a state change on the validation item, with the Board as owner.
- **Contract**:
  - The screen never writes anything except the Board's decision.
  - The decision lands in the record within one refresh and is visible to the trace tools.
  - Any item on screen shows its id, so the Board can quote it.
  - Nothing on screen requires reading code.
- **Checklist**:
  1. Written evaluation of at least two existing UIs against items 2 to 5, with the pick and the reason. [reasoning]
  2. List all intents with rollup: stories total, stories done, care level. [showing]
  3. Open an intent and see the forward trace as a tree. [showing]
  4. Open any leaf and see the back trace to its intent. [showing]
  5. Record yes or no on an intent; afterwards the decision appears in the record with the Board as owner. [showing]
- **Evaluation (item 1, 2026-09-04)**: beads-web reads `.beads/issues.jsonl`, which Dolt-mode beads does not produce, and has no tree or graph view: fails items 3 and 4 before install. beads-dashboard drives `bd` through subprocess and lists tree, graph, detail, status change and comments, so it was installed from GitHub and run against our record: the page renders blank with 67 identical `toLowerCase is not a function` errors in a minified bundle; the project has one commit and no version pin against beads 1.0. Fixing a stranger's minified frontend is not our work. **Pick: build our own, only the four things.**
- **Job pairs**: `board_rollup`, `board_tree`, `board_decide`, `board_page`, `board_serve`. Server is Python stdlib http.server, page is one HTML string, no framework, no build step.
- **Needs first**: 0001-2

### Story 0001-4: agents read and write the record through one skill

- **Parent Intent**: 0001
- **One thing it must do**: a role skill can say "read the record" and any harness does it.
- **Customer**: the Architect and Builder skills, and through them every model on every harness.
- **Supplier**: the Architect writes the skill file. Builders write the three missing wrapper functions.
- **Inputs**: a role skill's instruction such as "fetch the instruction sheet for job X".
- **Outputs**: `roles/work-record/SKILL.md` naming one exact command per operation. Each command returns JSON.
- **Contract**:
  - Exactly these operations, no more: create item, add link, list ready, show item, set state, set owner, add note.
  - Every command works with no network and no credentials.
  - Every command is one line a cheap model can copy without editing anything but the arguments.
  - No role skill names beads. Only the work-record skill does.
- **Checklist**:
  1. The skill file exists and lists the seven operations with exact commands. [looking]
  2. Every command returns machine-readable output. [testing]
  3. Board, Architect, and Builder skills reference the work-record skill and describe the record in no other words. [looking]
  4. A Builder given only a job id can fetch its instruction sheet using only the skill. [testing]
- **Job pairs**: `record_show_item`, `record_set_owner`, `record_add_note`. The skill file is a looking item, not a job.
- **Needs first**: 0001-1

### Story 0001-5: the log

- **Parent Intent**: 0001
- **One thing it must do**: an append-only log per policy section 10, separate from the record, one structured line per decision.
- **Customer**: the Supervisor writes it. The Board and the Architect read it when they need to trust a closure they did not see.
- **Supplier**: Builders.
- **Inputs**: append: timestamp, item id, gate, rule, raw inputs, resulting state. Read: an item id.
- **Outputs**: append: nothing on success, error on failure. Read: every line for that item, in write order, as JSON.
- **Contract**:
  - One line per call, one JSON object per line.
  - The write path can only append. There is no edit or delete function.
  - A line missing any of the six fields is rejected before it is written.
  - Reading never changes the file.
  - The log is git-tracked so history is also in git.
- **Checklist**:
  1. Append a full line and read it back by item id. [testing]
  2. Append with a missing field is rejected and nothing is written. [testing]
  3. Three appends for one id read back in order. [testing]
  4. The module exposes no function that edits or removes a line. [looking]
- **Job pairs**: `log_append`, `log_read_item`
- **Needs first**: none

## Order

0001-1 and 0001-5 first, in parallel. Then 0001-2 and 0001-4. Then 0001-3. The Board is shown 0001-3 last.

## Status

Stories 0001-1, 0001-2, 0001-4 and 0001-5 are Verified (2026-09-04, see work/supervisor-log.jsonl). Remaining: 0001-3, the Board screen. Environment note: this bd build has no embedded Dolt, so the record runs in server mode against a local dolt sql-server; tests start one per test via src/conftest.py. Next: sheets for 0001-2 and 0001-4. Instruction sheets are in `work/sheets/`. Language for all jobs: Python 3.12, tests with pytest. Chosen because the wrapper generator and the orphan tooling are already Python and every harness can run it.
