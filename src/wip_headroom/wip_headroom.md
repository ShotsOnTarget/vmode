purpose: compute remaining WIP capacity for a board column
signature: wip_headroom(name: str, graph: dict, config: dict) -> int
inputs: name (column name), graph (item graph), config (board config)
outputs: config['columns'][name]['wip'] minus in_progress items of that column's kinds, floored at 0
side effects: none
work item id: 0003-2-wip_headroom-code
