purpose: check a built code job against the gate rules and return broken rule names
signature: gate_built(job_id: str, inputs: dict) -> list[str]
inputs: job_id, and inputs dict with keys changed, code, note, fmt_out, lint_out
outputs: list of rule names broken, in fixed check order
side effects: none, pure function
work item id: 0003-1-gate_built-code
