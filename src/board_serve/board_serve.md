purpose: serve the board web UI and its API over HTTP
signature: board_serve(port: int) -> None
inputs: port to listen on, 127.0.0.1 only
outputs: serves forever; GET / -> board_page(); GET /api/intents -> board_rollup(record_graph(), care); GET /api/tree?id=X -> board_tree(X, record_graph()); POST /api/decide -> board_decide(...); unknown path -> 404
side effects: reads the record fresh on every request via record_run/record_graph; binds and listens on a local TCP socket
work item id: 0001-3-board_serve-code
