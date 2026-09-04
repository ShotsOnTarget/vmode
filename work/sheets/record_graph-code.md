# Instruction sheet

- **Job id**: 0001-2-record_graph-code
- **Kind**: code
- **Parent Story**: 0001-2
- **Function name**: `record_graph`
- **Folder**: `src/record_graph/`
- **Files you may change**: `src/record_graph/record_graph.py`, `src/record_graph/record_graph.md`
- **Signature**: `record_graph() -> dict[str, dict]`
- **Inputs**: none. Reads the whole record with record_run(['list','--all']).
- **Outputs**: dict keyed by id. Each value: {'id': str, 'kind': str, 'title': str, 'owner': str, 'state': str, 'parent': str | None, 'checks': list[str], 'needs': list[str]}. kind, state and owner come from labels 'kind:x', 'state:x' and 'owner:x' (first match, '' if none). Additionally 'claimed_by': the assignee or '' . parent: the item's 'parent' field if set, otherwise the depends_on_id of its first dependency of type 'validates', otherwise None. checks: ids this item has a dependency on with type 'validates'. needs: ids this item has a dependency on with type 'blocks'.
- **Errors**: RecordError propagates.
- **Allowed imports**: from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-2 items contract: one read of the record
- **How**: Each item in the list has a 'dependencies' list of {'issue_id','depends_on_id','type'}. Only read the record once.
- **Checks to run before reporting**:
  - `wc -l src/record_graph/record_graph.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/record_graph/record_graph.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/record_graph/record_graph.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-2-record_graph-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
