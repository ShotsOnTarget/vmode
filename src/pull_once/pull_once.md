purpose: pull ready items into a role's columns and invoke work on them
signature: pull_once(role: str, config_path: str, invoke) -> list[str]
inputs: role (role name in config), config_path (path to board config TOML), invoke (item: dict, column: str) -> dict with keys tokens, seconds, report; may raise
outputs: ids of items claimed this pass
side effects: claims items, calls invoke, adds usage/release notes, sets item state to checking/ready or (labels_absent columns) adds a label and clears the claim; skips items lost to a claim race
work item id: 0003-4-pull_once-code
