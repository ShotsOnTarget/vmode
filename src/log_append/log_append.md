purpose: append one JSON log entry as a line to a log file
signature: log_append(path: str, entry: dict) -> None
inputs: path: log file, created if missing. entry: dict with exactly the keys ts, item, gate, rule, inputs, state, tokens, seconds.
outputs: nothing
side effects: opens path in append mode and writes one line: json.dumps(entry, sort_keys=True) plus newline
work item id: 0002-1-log_append-code
