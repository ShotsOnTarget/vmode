from column_of.column_of import column_of


def column_items(
    name: str, graph: dict, labels: dict[str, list[str]], config: dict
) -> list[dict]:
    if name not in config["columns"]:
        raise ValueError(f"not a column: {name}")
    items = []
    for item_id, item in graph.items():
        if column_of(item, labels.get(item_id, []), config) != name:
            continue
        if any(graph.get(need, {}).get("state") != "done" for need in item["needs"]):
            continue
        items.append(item)
    return sorted(items, key=lambda i: i["id"])
