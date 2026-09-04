purpose: replay a work item's log lines through step to compute its final state
signature: replay_log(path: str, item_id: str) -> str
inputs: path (log file of JSON lines with keys ts, item, gate, rule, inputs, state; tokens, seconds optional), item_id (exact item to replay)
outputs: the final state after mapping each of the item's lines to an event and feeding step, in file order
side effects: none
work item id: 0003-3-replay_log-code
