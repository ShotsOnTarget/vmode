purpose: roll up token, second, and run counts for an item id and its descendants from a log file
signature: cost_rollup(path: str, item_id: str) -> dict
inputs: path: log file. item_id: an id such as '0001', '0001-1', or '0001-1-record_run-code'.
outputs: {'item': item_id, 'tokens': int, 'seconds': float, 'runs': int}
side effects: none, pure read
work item id: 0002-1-cost_rollup-code
