# Instruction sheet

- **Job id**: 0001-5-log_append-code
- **Kind**: code
- **Parent Story**: 0001-5
- **Function name**: `log_append`
- **Folder**: `src/log_append/`
- **Files you may change**: `src/log_append/log_append.py`, `src/log_append/log_append.md`
- **Signature**: `log_append(path: str, entry: dict) -> None`
- **Inputs**: path: log file, created if missing. entry: dict with exactly the keys ts, item, gate, rule, inputs, state. Values: ts ISO-8601 str, item str, gate str, rule str, inputs any JSON-serialisable, state str.
- **Outputs**: nothing. One line appended: json.dumps(entry, sort_keys=True) plus newline.
- **Errors**: raise ValueError, and write nothing, if any of the six keys is missing or extra keys are present.
- **Allowed imports**: json. Nothing else.
- **Checklist items this job serves**: Story 0001-5 items 1, 2, 4
- **How**: Open the file with mode 'a' only. Do not define any function that opens the file in any other write mode.
- **Checks to run before reporting**:
  - `wc -l src/log_append/log_append.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/log_append/log_append.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/log_append/log_append.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-5-log_append-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
