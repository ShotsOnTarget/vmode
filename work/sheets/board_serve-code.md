# Instruction sheet

- **Job id**: 0001-3-board_serve-code
- **Kind**: code
- **Parent Story**: 0001-3
- **Function name**: `board_serve`
- **Folder**: `src/board_serve/`
- **Files you may change**: `src/board_serve/board_serve.py`, `src/board_serve/board_serve.md`
- **Signature**: `board_serve(port: int) -> None`
- **Inputs**: port to listen on, 127.0.0.1 only.
- **Outputs**: serves forever. GET / -> board_page(). GET /api/intents -> JSON board_rollup(graph, care) where graph=record_graph() and care is read via record_run(['list','--all']) picking label care:x per intent. GET /api/tree?id=X -> JSON board_tree(X, record_graph()). POST /api/decide with JSON body {'intent': str, 'decision': str, 'reason': str} (exactly these keys, as sent by board_page) -> JSON board_decide(intent, decision, reason). Unknown path -> 404. Errors (ValueError, RecordError) -> 400 with {'error': str}.
- **Errors**: as above, never crashes the server.
- **Allowed imports**: json, http.server, urllib.parse, from board_page.board_page import board_page, from board_rollup.board_rollup import board_rollup, from board_tree.board_tree import board_tree, from board_decide.board_decide import board_decide, from record_graph.record_graph import record_graph, from record_run.record_run import record_run, RecordError. Nothing else.
- **Checklist items this job serves**: Story 0001-3 items 2, 3, 4, 5
- **How**: Use http.server.ThreadingHTTPServer with a BaseHTTPRequestHandler subclass defined inside board_serve (a nested class is not a public function). Read the record fresh on every request; no caching. Under 50 lines: keep handler methods tiny and use one helper closure for writing JSON.
- **Checks to run before reporting**:
  - `wc -l src/board_serve/board_serve.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/board_serve/board_serve.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/board_serve/board_serve.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-3-board_serve-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
