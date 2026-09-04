# Instruction sheet

- **Job id**:
- **Kind**: code or test.
- **Parent Story**:
- **Function name**: also the folder name and file stem.
- **Folder**: `src/<function name>/`
- **Files you may change**: exact list.
- **Signature**: exact.
- **Inputs**: type and meaning of each.
- **Outputs**: type and meaning.
- **Errors**: what happens on bad input.
- **Allowed imports**: exact list. Nothing else.
- **Checklist items this job serves**: ids from the Story.
- **Cases** (test jobs only): named list, one line each, with expected result.
- **Checks to run before reporting**: exact commands. Always includes, for the job's folder: the formatter (`ruff format src/<name>`), the linter (`ruff check src/<name>`), the shape checker (`python tools/lint.py`), and the tests.
- **Out of scope**: what not to do.
