purpose: dispatch HTTP requests to the board's route handlers
signature: board_routes(method: str, path: str, query: dict, body: dict) -> tuple[int, str, object]
inputs: method: 'GET' or 'POST'. path: URL path without query. query: parsed query parameters. body: parsed JSON body for POST, {} otherwise.
outputs: (status, content_type, payload) for the matched route, or (404, 'application/json', {'error': 'not found'}) if unmatched
side effects: none directly; delegates to board_api, which reads the record fresh and may update it via decide or release
work item id: 0001-3-board_routes-code
