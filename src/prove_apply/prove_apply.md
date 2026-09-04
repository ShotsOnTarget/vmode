purpose: compose gate rules, step the state machine, apply the move, and log one line per gate that ran.
signature: prove_apply(job_id: str, gathered: dict, log_path: str) -> str
inputs: job_id (record item id); gathered (dict from prove_gather plus 'folder'); log_path (Supervisor log file path).
outputs: the resulting state string from step.
side effects: calls prove_move to apply the state/bounce/escalate effects; appends one log line per gate (Built always, Proven when kind is 'test') to log_path.
work item id: 0003-4-prove_apply-code
