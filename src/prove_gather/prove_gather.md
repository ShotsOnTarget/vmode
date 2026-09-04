Purpose: gather a job's code, note, checks, and metadata for the Proven gate.
Signature: prove_gather(job_id: str, folder: str) -> dict
Inputs: job_id, the record id of a code or test job; folder, the function folder name.
Outputs: dict with changed, code, note, fmt_out, lint_out, pytest_out, cases, kind, usage, retries.
Side effects: calls record_graph and changed_paths (which run git status), `bd comments <id>` (exact command used for notes, falling back to `bd show <id>`), and runs ruff and pytest as subprocesses.
Work item id: 0003-4-prove_gather-code.
