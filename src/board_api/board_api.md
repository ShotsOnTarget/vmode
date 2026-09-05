purpose: dispatch one board API call by name to its handler
signature: board_api(name: str, query: dict, body: dict) -> object
inputs: name: one of intents, tree, item, columns, decide. query and body as parsed by the caller.
outputs: the JSON payload for the named API
side effects: none (reads the record fresh on every call)
work item id: 0001-3-board_api-code
