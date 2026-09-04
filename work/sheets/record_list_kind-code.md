# Instruction sheet

- **Job id**: 0001-1-record_list_kind-code
- **Kind**: code
- **Parent Story**: 0001-1
- **Function name**: `record_list_kind`
- **Folder**: `src/record_list_kind/`
- **Files you may change**: `src/record_list_kind/record_list_kind.py`, `src/record_list_kind/record_list_kind.md`
- **Signature**: `record_list_kind(kind: str) -> list[dict]`
- **Inputs**: kind: one of the six kinds.
- **Outputs**: list of {'id','kind','title','owner','state'} for every item with that kind label, including closed ones.
- **Errors**: raise ValueError if kind invalid. RecordError propagates.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-1 items 2
- **How**: Call record_run(['list','--all','-l',f'kind:{kind}']). Map the owner: label to owner and the state: label to state; never the assignee.
- **Checks to run before reporting**:
  - `wc -l src/record_list_kind/record_list_kind.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_list_kind/record_list_kind.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_list_kind/record_list_kind.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-1-record_list_kind-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
