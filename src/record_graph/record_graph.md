purpose: build a graph of the whole record keyed by item id
signature: record_graph() -> dict[str, dict]
inputs: none
outputs: dict keyed by id, each value {'id', 'kind', 'title', 'owner', 'state', 'parent', 'checks', 'needs', 'claimed_by'}
side effects: none (single read via record_run(['list', '--all']))
work item id: 0001-2-record_graph-code
