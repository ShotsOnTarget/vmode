purpose: apply a Supervisor step outcome to a job's record: set its state, and for 'bounce' add a note plus swap the retry label, or for 'escalate' also write a summary file.
signature: prove_move(job_id: str, outcome: dict) -> None
inputs: job_id (record item id); outcome (dict with 'action', 'state', 'retries', 'rules' from step).
outputs: none.
side effects: always sets the record item's state; on bounce adds a note and swaps the 'retry:' label; on escalate writes work/summaries/<job_id>.md.
work item id: 0003-4-prove_move-code
