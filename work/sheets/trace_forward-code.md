# Instruction sheet

- **Job id**: 0001-2-trace_forward-code
- **Kind**: code
- **Parent Story**: 0001-2
- **Function name**: `trace_forward`
- **Folder**: `src/trace_forward/`
- **Files you may change**: `src/trace_forward/trace_forward.py`, `src/trace_forward/trace_forward.md`
- **Signature**: `trace_forward(item_id: str, graph: dict[str, dict]) -> dict`
- **Inputs**: item_id and graph as for trace_back.
- **Outputs**: tree {'id','kind','title','children': [subtrees]}. children are every item whose parent is this id, plus every item whose checks list contains this id, in id order, no duplicates.
- **Errors**: raise ValueError if item_id not in graph. A cycle is broken by never visiting an id twice; it is not an error.
- **Allowed imports**: none. Nothing else.
- **Checklist items this job serves**: Story 0001-2 items 2
- **How**: Pure function. Recursive with a visited set passed down.
- **Checks to run before reporting**:
  - `wc -l src/trace_forward/trace_forward.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/trace_forward/trace_forward.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/trace_forward/trace_forward.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-2-trace_forward-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
