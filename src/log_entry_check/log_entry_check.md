purpose: validate a log entry dict before it is appended to the record
signature: log_entry_check(entry: dict) -> None
inputs: entry: dict with exactly the keys item, gate, rule, inputs, state, tokens, seconds, actor. tokens must be an int (not bool). seconds must be >= 0. actor must be non-empty.
outputs: None when the entry is valid
side effects: none
work item id: 0005-1-log_entry_check-code
