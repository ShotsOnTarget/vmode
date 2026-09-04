purpose: Check whether a story's items satisfy the graph rules needed to close it.
signature: gate_ready(story_id: str, graph: dict, sheets: dict[str, str]) -> list[str]
inputs: story_id: id in graph. graph: id -> item dict from record_graph. sheets: job id -> sheet text.
outputs: list of broken rule names, fixed order, empty if none.
side effects: none.
work item id: 0003-1-gate_ready-code
