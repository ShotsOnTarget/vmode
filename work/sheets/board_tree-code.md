# Instruction sheet

- **Job id**: 0001-3-board_tree-code
- **Kind**: code
- **Parent Story**: 0001-3
- **Function name**: `board_tree`
- **Folder**: `src/board_tree/`
- **Files you may change**: `src/board_tree/board_tree.py`, `src/board_tree/board_tree.md`
- **Signature**: `board_tree(item_id: str, graph: dict[str, dict]) -> dict`
- **Inputs**: an id in graph.
- **Outputs**: {'back': trace_back(item_id, graph), 'forward': trace_forward(item_id, graph)}.
- **Errors**: ValueError from either propagates.
- **Allowed imports**: from trace_back.trace_back import trace_back; from trace_forward.trace_forward import trace_forward. Nothing else.
- **Checklist items this job serves**: Story 0001-3 items 3, 4
- **How**: Composition only. Under ten lines.
- **Checks to run before reporting**:
  - `wc -l src/board_tree/board_tree.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/board_tree/board_tree.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/board_tree/board_tree.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-3-board_tree-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
