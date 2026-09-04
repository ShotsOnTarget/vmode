# Instruction sheet

- **Job id**: 0001-4-record_add_note-code
- **Kind**: code
- **Parent Story**: 0001-4
- **Function name**: `record_add_note`
- **Folder**: `src/record_add_note/`
- **Files you may change**: `src/record_add_note/record_add_note.py`, `src/record_add_note/record_add_note.md`
- **Signature**: `record_add_note(item_id: str, text: str) -> dict`
- **Inputs**: item_id existing; text non-empty.
- **Outputs**: {'id': item_id, 'note_id': str} where note_id comes from the comment's 'id' field.
- **Errors**: raise ValueError if text is empty. RecordError propagates.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-4 items 2
- **How**: record_run(['comment', item_id, text]).
- **Checks to run before reporting**:
  - `wc -l src/record_add_note/record_add_note.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_add_note/record_add_note.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_add_note/record_add_note.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-4-record_add_note-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
