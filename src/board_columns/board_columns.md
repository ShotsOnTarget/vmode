purpose: place every graph item into its board column
signature: board_columns(graph: dict, labels: dict, config: dict) -> list[dict]
inputs: graph (record_graph dict), labels (id -> label list), config (board_config dict)
outputs: one dict per column in config order: name, role, wip, in_progress count, items list
side effects: none
work item id: 0001-6-board_columns-code
