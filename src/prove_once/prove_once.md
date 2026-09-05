Purpose: run one pass of the prove step, gathering and applying gate checks for every job in the 'prove' column, then advance any story whose jobs are all done.
Signature: prove_once(config_path: str) -> list[str]
Inputs: config_path (roles/board.toml).
Outputs: the ids of the jobs processed, in order.
Side effects: runs prove_gather and prove_apply for each prove-column job (which run formatters/linters/tests and append to the log); calls record_set_state('checking') on newly-complete stories.
Work item id: 0003-4-prove_once-code
