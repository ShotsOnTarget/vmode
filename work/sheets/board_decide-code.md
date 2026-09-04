# Instruction sheet

- **Job id**: 0001-3-board_decide-code
- **Kind**: code
- **Parent Story**: 0001-3
- **Function name**: `board_decide`
- **Folder**: `src/board_decide/`
- **Files you may change**: `src/board_decide/board_decide.py`, `src/board_decide/board_decide.md`
- **Signature**: `board_decide(intent_id: str, decision: str, reason: str) -> dict`
- **Inputs**: intent_id: an intent in the record. decision: 'yes' or 'no'. reason: text, may be '' for yes, must be non-empty for no.
- **Outputs**: {'intent': intent_id, 'validation': validation_id, 'state': 'done' or 'reopened'}.
- **Errors**: ValueError if decision is not yes/no, or no is given with empty reason, or no validation item checks this intent. RecordError propagates.
- **Allowed imports**: from record_graph.record_graph import record_graph; from record_set_state.record_set_state import record_set_state; from record_set_owner.record_set_owner import record_set_owner; from record_add_note.record_add_note import record_add_note. Nothing else.
- **Checklist items this job serves**: Story 0001-3 items 5
- **How**: Find the validation: the item of kind validation whose checks list contains intent_id. yes -> set its state done. no -> set its state reopened. In both cases set its owner to 'board' and add a note 'board: yes' or 'board: no: <reason>'. This is the only write the Board screen ever makes.
- **Checks to run before reporting**:
  - `wc -l src/board_decide/board_decide.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/board_decide/board_decide.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/board_decide/board_decide.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-3-board_decide-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
