purpose: set an item's workflow state label and matching bd status
signature: record_set_state(item_id: str, state: str) -> dict
inputs: item_id (existing id), state (one of waiting, ready, in_progress, blocked, checking, done, reopened)
outputs: {'id': str, 'state': str}
side effects: removes existing state:* labels, adds new state label, updates bd status via record_run
work item id: 0001-1-record_set_state-code
