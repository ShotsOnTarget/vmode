# Instruction sheet

- **Job id**: 0001-1-record_create_item-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_create_item`
- **Folder**: `src/record_create_item/`
- **Files you may change**: `src/record_create_item/record_create_item.py`, `src/record_create_item/record_create_item.md`
- **Signature**: `record_create_item(kind: str, title: str, owner: str, parent: str | None = None) -> dict`
- **Inputs**: kind: one of intent, story, code, test, verification, validation, proposal. title: non-empty. owner: non-empty. parent: an existing id, required unless kind is intent. For the right-side kinds test, verification and validation, parent is the item this one checks.
- **Outputs**: {'id': str, 'kind': str, 'title': str, 'owner': str, 'parent': str | None, 'state': 'waiting'}. Owner is stored as the label owner:<owner>; the assignee is never set on create, it is the claim slot. Owner is stored as the label owner:<owner>; the assignee is never set on create, it is the claim slot.
- **Errors**: raise ValueError before calling bd if kind is not one of the seven, owner is empty, or parent is None and kind is not intent. RecordError propagates from record_run.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items 2, 3, 4
- **How**: Call record_run(['create', title, '-t', 'epic' if intent else 'task', '-l', f'kind:{kind},state:waiting,owner:{owner}', '--no-inherit-labels'] + (['--parent', parent] if parent else [])). The --no-inherit-labels flag is mandatory: without it a child copies its parent's kind label. proposal is a left-side kind and takes --parent like story and code. For kinds test, verification and validation do NOT pass --parent; instead, after the create, call record_run(['dep','add',new_id,parent,'-t','validates']). beads refuses a validates link between a hierarchical child and its parent, so right-side items are attached by the validates link only. Return 'parent': parent in both cases. Read the id from the returned dict.
- **Checks to run before reporting**:
  - `wc -l src/record_create_item/record_create_item.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_create_item/record_create_item.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_create_item/record_create_item.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_create_item-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
