purpose: Read a JSON-lines log file and return every entry matching a given item id.
signature: log_read_item(path: str, item_id: str) -> list[dict]
inputs: path: log file. item_id: value to match on the 'item' key.
outputs: every entry whose item equals item_id, in file order. [] if file missing.
side effects: none (read-only)
work item id: 0001-5-log_read_item-code
