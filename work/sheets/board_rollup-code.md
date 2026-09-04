# Instruction sheet

- **Job id**: 0001-3-board_rollup-code
- **Kind**: code
- **Parent Story**: 0001-3
- **Function name**: `board_rollup`
- **Folder**: `src/board_rollup/`
- **Files you may change**: `src/board_rollup/board_rollup.py`, `src/board_rollup/board_rollup.md`
- **Signature**: `board_rollup(graph: dict[str, dict], care: dict[str, str]) -> list[dict]`
- **Inputs**: graph from record_graph. care: mapping intent id -> 'high' or 'low' (the caller reads it from the care: label; record_graph does not expose labels).
- **Outputs**: one dict per intent, id order: {'id','title','state','care','stories_total','stories_done'}. stories are items of kind story whose parent is the intent; done means state == 'done'.
- **Errors**: none. Intent missing from care gets care ''.
- **Allowed imports**: none. Nothing else.
- **Checklist items this job serves**: Story 0001-3 items 2
- **How**: Pure function.
- **Checks to run before reporting**:
  - `wc -l src/board_rollup/board_rollup.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/board_rollup/board_rollup.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/board_rollup/board_rollup.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-3-board_rollup-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
