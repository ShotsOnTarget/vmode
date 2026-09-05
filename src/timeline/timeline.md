purpose: return the log events for an item and everything under it, in time order.
signature: timeline(item_id: str, graph: dict) -> list[dict]
inputs: item_id in graph; graph from record_graph.
outputs: log entries (same dict shape as log_read_item) for item_id and its full descendant tree (by parent, or by checks), sorted by ts.
side effects: none (read-only; reads work/supervisor-log.jsonl)
work item id: 0005-1-timeline-code
