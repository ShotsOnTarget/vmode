purpose: walk the parent chain of an item to its root, returning the path
signature: trace_back(item_id: str, graph: dict[str, dict]) -> list[dict]
inputs: item_id: an id present in graph. graph: output of record_graph.
outputs: list of {'id','kind','title'} starting at item_id and following parent until an item with no parent, that item last.
side effects: none
work item id: 0001-2-trace_back-code
