purpose: compose gate rules, step the state machine, apply the move, and log one line per gate that ran.
signature: prove_apply(job_id: str, gathered: dict) -> str
inputs: job_id (record item id); gathered (dict from prove_gather plus 'folder').
outputs: the resulting state string from step.
side effects: calls prove_move to apply the state/bounce/escalate effects; on action 'log_done' calls commit_job to land the change; calls log_append once per gate that ran (Built always, Proven when kind is 'test').
work item id: 0003-4-prove_apply-code
