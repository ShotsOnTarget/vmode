# Instruction sheet

- **Job id**: 0001-1-record_init-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_init`
- **Folder**: `src/record_init/`
- **Files you may change**: `src/record_init/record_init.py`, `src/record_init/record_init.md`
- **Signature**: `record_init(path: str) -> dict`
- **Inputs**: path: an existing empty directory.
- **Outputs**: {'path': str, 'prefix': 'vm'}.
- **Errors**: raise RecordError if the directory does not exist, or bd init fails.
- **Allowed imports**: subprocess, os, from record_run.record_run import RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items 1
- **How**: Run exactly: bd init --prefix vm --non-interactive, with cwd=path. Do not pass --force.
- **Checks to run before reporting**:
  - `wc -l src/record_init/record_init.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_init/record_init.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_init/record_init.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_init-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
