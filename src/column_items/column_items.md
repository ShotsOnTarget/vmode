purpose: list the items belonging to a given board column, in id order
signature: column_items(name: str, graph: dict, labels: dict[str, list[str]], config: dict) -> list[dict]
inputs: name (column name in config), graph (id -> item dict), labels (id -> label list), config (board config dict)
outputs: items whose column_of(...) == name, excluding any item with an unmet 'needs' entry, ordered by id
side effects: none
work item id: 0003-2-column_items-code
