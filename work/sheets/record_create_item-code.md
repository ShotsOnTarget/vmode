# Instruction sheet

- **Job id**: 0001-1-record_create_item-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_create_item`
- **Folder**: `src/record_create_item/`
- **Files you may change**: `src/record_create_item/record_create_item.py`, `src/record_create_item/record_create_item.md`
- **Signature**: `record_create_item(kind: str, title: str, owner: str, parent: str | None = None) -> dict`
- **Inputs**: kind: one of intent, story, code, test, verification, validation. title: non-empty. owner: non-empty. parent: an existing id, required unless kind is intent.
- **Outputs**: {'id': str, 'kind': str, 'title': str, 'owner': str, 'parent': str | None, 'state': 'waiting'}.
- **Errors**: raise ValueError before calling bd if kind is not one of the six, owner is empty, or parent is None and kind is not intent. RecordError propagates from record_run.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items 2, 3, 4
- **How**: Call record_run(['create', title, '-t', 'epic' if intent else 'task', '-l', f'kind:{kind},state:waiting', '-a', owner, '--no-inherit-labels'] + (['--parent', parent] if parent else [])). The --no-inherit-labels flag is mandatory: without it a child copies its parent's kind label. Read the id from the returned dict.
- **Checks to run before reporting**:
  - `wc -l src/record_create_item/record_create_item.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_create_item/record_create_item.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_create_item/record_create_item.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_create_item-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
