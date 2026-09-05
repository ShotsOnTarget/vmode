purpose: serve HTTP requests for the board, delegating all routing to board_routes
signature: board_serve(port: int) -> None
inputs: port to listen on, 127.0.0.1 only
outputs: serves forever; for each request parses path, query and JSON body, calls board_routes(method, path, query, body), and writes the returned status, content type and payload
side effects: reads the record fresh on every request via board_routes; binds and listens on a local TCP socket
work item id: 0001-3-board_serve-code
