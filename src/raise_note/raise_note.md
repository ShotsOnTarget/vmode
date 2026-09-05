purpose: create a note item under a job, with the Supervisor's escalation summary as its description, for a bounce or an escalate
signature: raise_note(job_id: str, outcome: dict) -> str
inputs: job_id (record item id); outcome (dict with 'action', 'state', 'retries', 'rules' from prove_move).
outputs: the new note item's id.
side effects: creates a 'note' item via record_create_item, then sets its description via record_run(['update', ..., '--body-file', ...]).
work item id: 0005-2-raise_note-code
