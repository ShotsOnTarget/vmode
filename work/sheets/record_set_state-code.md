# Instruction sheet

- **Job id**: 0001-1-record_set_state-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_set_state`
- **Folder**: `src/record_set_state/`
- **Files you may change**: `src/record_set_state/record_set_state.py`, `src/record_set_state/record_set_state.md`
- **Signature**: `record_set_state(item_id: str, state: str) -> dict`
- **Inputs**: item_id: existing id. state: one of waiting, ready, in_progress, blocked, checking, done, reopened.
- **Outputs**: {'id': str, 'state': str}.
- **Errors**: raise ValueError before calling bd if state is not one of the seven. RecordError propagates.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items 6
- **How**: Mapping to bd status: waiting/ready/checking/reopened -> open, in_progress -> in_progress, blocked -> blocked, done -> closed. Do three calls: record_run(['label','remove',item_id,'state:*']) is not available, so first read labels with ['label','list',item_id], remove any label starting with 'state:', then ['label','add',item_id,f'state:{state}'], then ['update',item_id,'-s',<status>].
- **Checks to run before reporting**:
  - `wc -l src/record_set_state/record_set_state.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_set_state/record_set_state.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_set_state/record_set_state.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_set_state-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
