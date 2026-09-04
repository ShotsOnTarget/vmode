# Instruction sheet

- **Job id**: 0001-4-record_show_item-code
- **Kind**: code
- **Parent Story**: 0001-4
- **Function name**: `record_show_item`
- **Folder**: `src/record_show_item/`
- **Files you may change**: `src/record_show_item/record_show_item.py`, `src/record_show_item/record_show_item.md`
- **Signature**: `record_show_item(item_id: str) -> dict`
- **Inputs**: item_id: existing id.
- **Outputs**: {'id','kind','title','owner','state','parent','sheet'} where sheet is the description text ('' if none).
- **Errors**: RecordError propagates for an unknown id.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-4 items 2, 4
- **How**: record_run(['show', item_id]) returns a one-element list. kind and state from labels as in record_graph.
- **Checks to run before reporting**:
  - `wc -l src/record_show_item/record_show_item.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_show_item/record_show_item.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_show_item/record_show_item.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-4-record_show_item-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
