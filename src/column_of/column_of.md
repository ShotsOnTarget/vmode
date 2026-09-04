purpose: determine which board column a graph item belongs in
signature: column_of(item: dict, labels: list[str], config: dict) -> str | None
inputs: item (graph item dict with 'kind' and 'state'), labels (list of the item's labels), config (board_config dict of columns and limits)
outputs: the matching column name, or None if no column matches
side effects: none
work item id: 0003-2-column_of-code
