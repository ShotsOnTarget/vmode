# Instruction sheet

- **Job id**: 0002-1-log_append-code
- **Kind**: code (reopen of an existing job)
- **Parent Story**: 0002-1
- **Function name**: `log_append`
- **Folder**: `src/log_append/`
- **Files you may change**: `src/log_append/log_append.py`, `src/log_append/log_append.md`
- **Signature**: `log_append(path: str, entry: dict) -> None`
- **Inputs**: path: log file, created if missing. entry: dict with exactly the keys ts, item, gate, rule, inputs, state, tokens, seconds. tokens: int, -1 means unknown. seconds: float >= 0.
- **Outputs**: nothing. One line appended: json.dumps(entry, sort_keys=True) plus newline.
- **Errors**: raise ValueError, and write nothing, if any of the eight keys is missing, extra keys are present, tokens is not an int, or seconds is negative.
- **Allowed imports**: json. Nothing else.
- **Checklist items this job serves**: Story 0002-1 items 1
- **How**: Open the file with mode 'a' only. This is a reopen of an existing job: two new required keys, tokens and seconds. Keep the existing behaviour otherwise.
- **Checks to run before reporting**:
  - `wc -l src/log_append/log_append.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/log_append/log_append.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/log_append/log_append.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0002-1-log_append-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
