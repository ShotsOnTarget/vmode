# Record conventions

How each policy section 4 field maps onto beads 1.0. This is the only document that knows the record is beads. Prefix for all ids: `vm`.

| Policy field | beads | Command |
|---|---|---|
| Id | issue id, `vm-xxxx`, permanent | assigned on create |
| Kind | label `kind:<kind>`; type `epic` for intent, `task` for the rest | `bd create -l kind:story -t task` |
| Parent | hierarchical parent | `bd create --parent <id>` or `bd dep add <child> <parent> -t parent-child` |
| Link: parent_of | dependency type `parent-child` | `bd dep add <child> <parent> -t parent-child` |
| Link: needs_first | dependency type `blocks` | `bd dep add <item> --blocked-by <other>` |
| Link: checks | dependency type `validates` (native, no label needed) | `bd dep add <checker> <checked> -t validates` |
| Owner | assignee, required | `bd create -a <owner>` |
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

Every command used by tools takes `--json`. Every wrapper function shells out to `bd`, never touches the database directly.
