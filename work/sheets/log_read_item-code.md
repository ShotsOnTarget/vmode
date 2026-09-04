# Instruction sheet

- **Job id**: 0001-5-log_read_item-code
- **Kind**: code
- **Parent Story**: 0001-5
- **Function name**: `log_read_item`
- **Folder**: `src/log_read_item/`
- **Files you may change**: `src/log_read_item/log_read_item.py`, `src/log_read_item/log_read_item.md`
- **Signature**: `log_read_item(path: str, item_id: str) -> list[dict]`
- **Inputs**: path: log file. item_id: value to match on the 'item' key.
- **Outputs**: every entry whose item equals item_id, in file order. [] if file missing.
- **Errors**: raise ValueError if any line is not valid JSON.
- **Allowed imports**: json, os. Nothing else.
- **Checklist items this job serves**: Story 0001-5 items 3
- **How**: Open the file read-only. Never write.
- **Checks to run before reporting**:
  - `wc -l src/log_read_item/log_read_item.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/log_read_item/log_read_item.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/log_read_item/log_read_item.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-5-log_read_item-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
