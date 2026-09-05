purpose: roll up token, second, and run counts over an item's full timeline
signature: cost_rollup(item_id: str, graph: dict) -> dict
inputs: item_id in graph; graph from record_graph.
outputs: {'item': item_id, 'tokens': int, 'seconds': float, 'runs': int} summed over timeline(item_id, graph)
side effects: none, pure read (via timeline, reads work/supervisor-log.jsonl)
work item id: 0005-1-cost_rollup-code
