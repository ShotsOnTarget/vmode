purpose: build the forward-trace tree of items descending from a given item id
signature: trace_forward(item_id: str, graph: dict[str, dict]) -> dict
inputs: item_id and graph as for trace_back
outputs: tree {'id','kind','title','children': [subtrees]}, children being every item whose parent is this id or whose checks list contains this id, in id order, no duplicates
side effects: none
work item id: 0001-2-trace_forward-code
