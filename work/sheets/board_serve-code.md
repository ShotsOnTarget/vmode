# Instruction sheet

- **Job id**: 0001-3-board_serve-code
- **Kind**: code
- **Parent Story**: 0001-3
- **Function name**: `board_serve`
- **Folder**: `src/board_serve/`
- **Files you may change**: `src/board_serve/board_serve.py`, `src/board_serve/board_serve.md`
- **Signature**: `board_serve(port: int) -> None`
- **Inputs**: port to listen on, 127.0.0.1 only.
- **Outputs**: serves forever on 127.0.0.1:port. For every request: parse the path and query with urllib.parse, parse a JSON body for POST, call board_routes(method, path, query, body) and write its status, content type and payload (JSON-encoded unless the content type is text/html). No route logic here.
- **Errors**: as above, never crashes the server.
- **Allowed imports**: json, http.server, urllib.parse, from board_routes.board_routes import board_routes. Nothing else.
- **Checklist items this job serves**: Story 0001-3 items 2, 3, 4, 5
- **How**: Use http.server.ThreadingHTTPServer with a BaseHTTPRequestHandler subclass defined inside board_serve (a nested class is not a public function). Read the record fresh on every request; no caching. Under 40 lines now that routing lives in board_routes.
- **Checks to run before reporting**:
  - `wc -l src/board_serve/board_serve.py   (must print 50 or less)`
  - `python -c "import ast,sys; t=ast.parse(open('src/board_serve/board_serve.py').read()); print(sum(isinstance(x,ast.FunctionDef) and not x.name.startswith('_') for x in t.body))"`   (must print 1)
- **Note file** `src/board_serve/board_serve.md` has exactly these six lines: purpose, signature, inputs, outputs, side effects, work item id 0001-3-board_serve-code.
- **Out of scope**: tests (another Builder writes them), any other folder, any import not listed, any behaviour not listed above.
