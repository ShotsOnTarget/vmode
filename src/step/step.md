purpose: compute the next policy transition for a work item
signature: step(state: str, event: str, retries: int) -> tuple[str, str, int]
inputs: state (one of the seven policy states), event (one of gate_pass, gate_fail, sheet_changed, claim_timeout, edited, claimed, ready_gate_pass, needs_done), retries (current count >= 0)
outputs: (action, next_state, new_retries) looked up from TABLE, with gate_fail retry arithmetic applied
side effects: none
work item id: 0003-3-step-code
