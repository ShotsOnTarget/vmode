purpose: roll up each intent with its care label and story completion counts
signature: board_rollup(graph: dict[str, dict], care: dict[str, str]) -> list[dict]
inputs: graph from record_graph. care: mapping intent id -> 'high' or 'low'
outputs: list of dicts, id order: {'id','title','state','care','stories_total','stories_done'}
side effects: none
work item id: 0001-3-board_rollup-code
