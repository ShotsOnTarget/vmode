# Record conventions

How each policy section 4 field maps onto beads 1.0. This is the only document that knows the record is beads. Prefix for all ids: `vm`.

| Policy field | beads | Command |
|---|---|---|
| Id | issue id, `vm-xxxx`, permanent | assigned on create |
| Kind | label `kind:<kind>`; type `epic` for intent, `task` for the rest | `bd create -l kind:story -t task` |
| Parent, left-side kinds (intent, story, code) | hierarchical parent | `bd create --parent <id>` |
| Parent, right-side kinds (validation, verification, test) | the item it checks, via the `validates` link only. Never `--parent`: beads refuses a validates link between a child and its parent. | `bd dep add <checker> <checked> -t validates` |
| Link: parent_of | dependency type `parent-child` | `bd dep add <child> <parent> -t parent-child` |
| Link: needs_first | dependency type `blocks` | `bd dep add <item> --blocked-by <other>` |
| Link: checks | dependency type `validates` (native, no label needed) | `bd dep add <checker> <checked> -t validates` |
| Owner | assignee, required | `bd create -a <owner>` |
| Care level (intents only) | label `care:low` or `care:high` | `bd label add <id> care:high` |
| State | label `state:<state>` is the source of truth, plus bd status kept in step | see table below |
| Checklist | acceptance field | `bd create --acceptance "..."` |
| Instruction sheet | description field | `bd create --body-file sheet.md` |
| History | Dolt commit per change, `bd show <id> --as-of <commit>`; JSONL export committed to git | `bd export > .beads/export.jsonl` |
| Note | comment | `bd comment <id> "..."` |

State mapping. The wrapper always sets both.

| Policy state | label | bd status |
|---|---|---|
| waiting | state:waiting | open |
| ready | state:ready | open |
| in_progress | state:in_progress | in_progress |
| blocked | state:blocked | blocked |
| checking | state:checking | open |
| done | state:done | closed |
| reopened | state:reopened | open |

"Ready" in beads (`bd list --ready`) is computed from blockers. Our `state:ready` label is set by the Supervisor only after the Ready gate passes. They are not the same thing.

Kinds, left and right of the V:

| Left | Right (checks the left) |
|---|---|
| intent | validation |
| story | verification |
| code | test |
| proposal | verification (Low care) or validation (High care) |

A proposal is a left-side kind: hierarchical child of the Story it learned from, label `kind:proposal`, sheet field in the shape of `roles/shared/proposal-format.md`.

Reading the parent: a left-side item's parent is its hierarchical parent. A right-side item's parent is the target of its validates link. `record_graph` applies this rule so trace and orphan tools see one parent for every item.

Every command used by tools takes `--json`. Every wrapper function shells out to `bd`, never touches the database directly.
