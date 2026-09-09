# Instruction sheet

A sheet is a contract, not a recipe. It says what the function must do and how it will be checked, and nothing about how to write it. The Builder decides the how within the shape rules, which the one check enforces.

- **Job id**:
- **Kind**: code or test.
- **Parent Story**:
- **Function name**: also the folder name and file stem.
- **Change** (only when that function already exists): what changes about it. A sheet naming a function already in the codebase map, with no Change field, is refused as `exists_without_change`: without it a Builder cannot tell a new function from a rewrite of one that already works, and has rewritten the working one.
- **Folder**: `src/<function name>/`
- **Signature**: exact.
- **Inputs**: type and meaning of each.
- **Outputs**: type and meaning; errors on bad input.
- **Facts**: one line per Boundary the Engineer probed: the fact itself, then where it came from in brackets, for example `prove_move passes the outcome dict through to raise_note unchanged (prove_move.py)`. A Builder reads these instead of opening files outside its folder. On a change to an existing function the field must be filled; an empty one is refused as `no_facts`.
- **Checklist items this job serves**: ids from the Story.
- **Cases** (test jobs only): one line per test function, `- \`test_name\`: expected result`. A case the sheet retires is written `- \`test_name\`: removed, <why>`; the gate then expects it gone.

Never on a sheet: allowed imports, helper structure, line counts, check commands, or a list of what not to touch. Those are the Builder skill's and the linter's. A Builder that needs a second folder says so in its report; the Supervisor raises the job.
