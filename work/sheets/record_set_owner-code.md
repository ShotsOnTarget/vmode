# Instruction sheet

- **Job id**: 0001-4-record_set_owner-code
- **Kind**: code
- **Parent Story**: 0001-4
- **Function name**: `record_set_owner`
- **Folder**: `src/record_set_owner/`
- **Files you may change**: `src/record_set_owner/record_set_owner.py`, `src/record_set_owner/record_set_owner.md`
- **Signature**: `record_set_owner(item_id: str, owner: str) -> dict`
- **Inputs**: item_id existing; owner non-empty.
- **Outputs**: {'id': item_id, 'owner': owner}. Implemented as a label swap: remove every label starting 'owner:' then add owner:<owner>. Never touches the assignee.
- **Errors**: raise ValueError if owner is empty, before calling bd. RecordError propagates.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-4 items 2
- **How**: record_run(['label','list',item_id]) returns a list of label strings; remove each 'owner:*' with record_run(['label','remove',item_id,label]); then record_run(['label','add',item_id,f'owner:{owner}']).
- **Checks to run before reporting**:
  - `wc -l src/record_set_owner/record_set_owner.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_set_owner/record_set_owner.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_set_owner/record_set_owner.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-4-record_set_owner-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
