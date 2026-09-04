purpose: compose gate_built and gate_proven results for a gathered job
signature: prove_rules(gathered: dict) -> list[str]
inputs: gathered dict with folder, kind, changed, code, note, fmt_out, lint_out, pytest_out, cases
outputs: list of gate_built findings, plus gate_proven findings when kind == 'test'
side effects: none
work item id: 0003-4-prove_rules-code
