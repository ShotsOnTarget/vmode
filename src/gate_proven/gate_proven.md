purpose: Check pytest output and case list against the proven gate rules.
signature: gate_proven(job_id: str, pytest_output: str, cases: list[str]) -> list[str]
inputs: job_id: string; pytest_output: text from `python -m pytest src/<folder> -q -rA`; cases: case names without the 'test_' prefix.
outputs: list of broken rules in fixed order: 'tests_failed', 'case_missing', 'case_extra'; empty list when all pass and names match exactly.
side effects: none.
work item id: 0003-1-gate_proven-code
