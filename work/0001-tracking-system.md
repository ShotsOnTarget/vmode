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
| Kind, parent, links | Issue types plus labels; parent-child, blocks, related, discovered-from | No "checks" link type. Map: right-side item is a child of the item it checks, labelled `checks`. |
| One owner | Assignee | None |
| Fixed states | open, in_progress, blocked, closed; "ready" is computed from blockers | "checking" and "reopened" become labels |
| Append-only history | JSONL in git; every change is a commit | Good enough for the record. The Supervisor log stays a separate append-only file. |
| Trace both ways | Dependency graph, `bd ready`, tree views | Orphan check is a small script, not built in |
| Agents read directly | CLI with JSON output, MCP server | None. CLI is the harness-neutral path. |

Not chosen: a hosted tracker (agents need auth and network, audit trail is theirs not ours), a hand-rolled SQLite app (rebuilds what beads already has).

Frontend: **adopt an existing beads web UI before building one.** Candidates with a running web server and a read view: beads-dashboard (tree, activity feed, kanban, graph, live updates), beads-web (kanban, epics, multi-project). Story 0001-3 evaluates them against the four things the Board actually does. Build our own only if both fail, and then only those four things.

Agent access: one skill, `work-record`, that wraps the CLI. Every role skill points at it instead of naming the tool. Keeps the policy line: skills describe "read the record", the work-record skill knows it is beads.

## Escalations to the Board

Judgement calls I will not make alone:

1. The record lives inside the git repo. Fine for one project. If we want one record across many repos later, that is a different choice. Accept for now?
2. The "checks" link is a convention (child plus label), not enforced by the tool. The orphan script enforces it. Accept, or require a tool that has the link natively?
3. Board screen will be third-party code we do not control. Accept, given it is read-mostly?

## Stories

### Story 0001-1: the record exists and holds the six kinds

- **Parent Intent**: 0001
- **One thing it must do**: a fresh checkout can create, link, and list all six item kinds with owner and state.
- **Checklist**:
  1. `init` in a clean folder produces a record with no items. [testing]
  2. Each of the six kinds can be created with a label naming the kind, and listed back filtered by kind. [testing]
  3. Parent-of, needs-first, and checks links can be added and read back. [testing]
  4. Every item has exactly one owner or the create is rejected. [testing]
  5. A convention document says how each policy field maps to a record field. [looking]
- **Job pairs**: `record_init`, `record_create_item`, `record_add_link`, `record_list_kind`
- **Needs first**: none

### Story 0001-2: trace both ways and find orphans

- **Parent Intent**: 0001
- **One thing it must do**: given any id, walk up to its Intent and down to every leaf, and report any orphan in the whole record.
- **Checklist**:
  1. Trace back from a code job returns the chain job, Story, Intent. [testing]
  2. Trace forward from an Intent returns every Story, pair, and check under it. [testing]
  3. A left-side item with nothing checking it is reported. [testing]
  4. A right-side item checking nothing is reported. [testing]
  5. An item with no parent that is not an Intent is reported. [testing]
  6. A clean record reports zero orphans and exits success. [testing]
- **Job pairs**: `trace_back`, `trace_forward`, `find_orphans`
- **Needs first**: 0001-1

### Story 0001-3: the Board screen

- **Parent Intent**: 0001
- **One thing it must do**: the Board can do its four jobs on a screen without a terminal.
- **Checklist**:
  1. List all Intents with a rollup: how many Stories, how many done, care level. [showing]
  2. Open an Intent and see the forward trace as a tree. [showing]
  3. Open any leaf and see the back trace to its Intent. [showing]
  4. Record yes or no on an Intent, with the decision visible in the record afterwards. [showing]
  5. Written evaluation of at least two existing UIs against items 1 to 4, with the pick and the reason. [reasoning]
- **Job pairs**: none if an existing UI passes. If not: `board_list_intents`, `board_show_tree`, `board_record_decision`, plus a page shell. Decided after item 5.
- **Needs first**: 0001-2

### Story 0001-4: agents read and write the record through one skill

- **Parent Intent**: 0001
- **One thing it must do**: a role skill can say "read the record" and any harness does it.
- **Checklist**:
  1. `roles/work-record/SKILL.md` exists, lists the exact commands for: create item, add link, list ready, show item, set state, set owner, add note. [looking]
  2. Every command returns machine-readable output. [testing]
  3. Board, Architect, and Builder skills reference the work-record skill and no longer describe the record in their own words. [looking]
  4. A Builder given a job id can fetch its instruction sheet from the record using only the skill. [testing]
- **Job pairs**: `record_show_item`, `record_set_state`, `record_add_note`. The skill file is a looking item, not a job.
- **Needs first**: 0001-1

### Story 0001-5: the log

- **Parent Intent**: 0001
- **One thing it must do**: an append-only log per policy section 10, separate from the record, with one structured line per decision.
- **Checklist**:
  1. Append a line with timestamp, item id, gate, rule, raw inputs, resulting state. [testing]
  2. Lines cannot be edited or removed by the normal write path. [testing]
  3. Filter the log by item id and get every line for that item in order. [testing]
- **Job pairs**: `log_append`, `log_read_item`
- **Needs first**: none

## Order

0001-1 and 0001-5 first, in parallel. Then 0001-2 and 0001-4. Then 0001-3. The Board is shown 0001-3 last.
