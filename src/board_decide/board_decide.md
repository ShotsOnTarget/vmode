purpose: record the board's yes/no decision on an intent by updating the validation item that checks it
signature: board_decide(intent_id: str, decision: str, reason: str) -> dict
inputs: intent_id: an intent in the record. decision: 'yes' or 'no'. reason: text, may be '' for yes, must be non-empty for no.
outputs: {'intent': intent_id, 'validation': validation_id, 'state': 'done' or 'reopened'}
side effects: sets the matching validation item's state (done or reopened) and owner (board), and adds a note recording the decision
work item id: 0001-3-board_decide-code
