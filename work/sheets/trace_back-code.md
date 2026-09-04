# Instruction sheet

- **Job id**: 0001-2-trace_back-code
- **Kind**: code
- **Parent Story**: 0001-2
- **Function name**: `trace_back`
- **Folder**: `src/trace_back/`
- **Files you may change**: `src/trace_back/trace_back.py`, `src/trace_back/trace_back.md`
- **Signature**: `trace_back(item_id: str, graph: dict[str, dict]) -> list[dict]`
- **Inputs**: item_id: an id present in graph. graph: output of record_graph.
- **Outputs**: list of {'id','kind','title'} starting at item_id and following parent until an item with no parent, that item last.
- **Errors**: raise ValueError if item_id is not in graph. raise ValueError('cycle') if an id repeats while walking.
- **Allowed imports**: none. Nothing else.
- **Checklist items this job serves**: Story 0001-2 items 1
- **How**: Pure function, no bd calls. Track visited ids in a set.
- **Checks to run before reporting**:
  - `wc -l src/trace_back/trace_back.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/trace_back/trace_back.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/trace_back/trace_back.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-2-trace_back-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
