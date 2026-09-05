purpose: claim an item and run invoke on it, handling the checking/label/release transitions
signature: claim_and_run(item: dict, column: str, role: str, options: dict) -> bool
inputs: item (from record_graph), column name, role, options with keys config (from board_config) and invoke (callable invoke(item, column) -> usage dict; may raise)
outputs: True when this puller claimed the item and ran invoke; False when another puller claimed it first
side effects: claims the item, adds usage/release notes, sets state to checking/ready or (labels_absent columns) adds a label and clears the claim
work item id: 0003-4-claim_and_run-code
