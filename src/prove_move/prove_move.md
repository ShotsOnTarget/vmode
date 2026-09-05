purpose: apply a Supervisor step outcome to a job's record: set its state, and for 'bounce' add a comment plus swap the retry label, or for 'escalate' just clear the claim; both call raise_note.
signature: prove_move(job_id: str, outcome: dict) -> None
inputs: job_id (record item id); outcome (dict with 'action', 'state', 'retries', 'rules' from step).
outputs: none.
side effects: always sets the record item's state; on bounce or escalate clears the claim and calls raise_note(job_id, outcome); bounce also adds a comment and swaps the 'retry:' label.
work item id: 0005-2-prove_move-code
