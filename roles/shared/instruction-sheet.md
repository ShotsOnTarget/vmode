# Instruction sheet

A sheet is a contract, not a recipe. It says what the function must do and how it will be checked, and nothing about how to write it. The Builder decides the how within the shape rules, which the one check enforces.

- **Job id**:
- **Kind**: code or test.
- **Parent Story**:
- **Function name**: also the folder name and file stem.
- **Folder**: `src/<function name>/`
- **Signature**: exact.
- **Inputs**: type and meaning of each.
- **Outputs**: type and meaning; errors on bad input.
- **Checklist items this job serves**: ids from the Story.
- **Cases** (test jobs only): one line per test function, `- \`test_name\`: expected result`. A case the sheet retires is written `- \`test_name\`: removed, <why>`; the gate then expects it gone.

Never on a sheet: allowed imports, helper structure, line counts, check commands, or a list of what not to touch. Those are the Builder skill's and the linter's. A Builder that needs a second folder says so in its report; the Supervisor raises the job.
