purpose: derive (from_state, event) transitions for one item from a JSON-lines log
signature: log_events(path: str, item_id: str) -> list[tuple[str, str]]
inputs: path: log file of JSON lines with keys ts, item, gate, rule, inputs, state. item_id: exact item.
outputs: list of (from_state, event) tuples in file order for matching lines, first matching rule wins
side effects: none, pure read of the file at path
work item id: 0003-3-log_events-code
