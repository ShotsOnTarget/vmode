# Instruction sheet

- **Job id**: 0001-1-record_run-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_run`
- **Folder**: `src/record_run/`
- **Files you may change**: `src/record_run/record_run.py`, `src/record_run/record_run.md`
- **Signature**: `record_run(args: list[str]) -> dict | list`
- **Inputs**: args: the bd arguments after the program name, e.g. ['show', 'vm-1']. `--json` is appended by this function, never by the caller.
- **Outputs**: the parsed JSON that bd printed on stdout.
- **Errors**: raise RecordError(message: str, stderr: str) if bd is not on PATH, exits non-zero, or prints non-JSON.
- **Allowed imports**: subprocess, json, shutil. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items contract: output JSON, errors JSON
- **How**: Define `class RecordError(Exception)` in this file. Every other record_* function imports it from here.
- **Checks to run before reporting**:
  - `wc -l src/record_run/record_run.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_run/record_run.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_run/record_run.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_run-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
