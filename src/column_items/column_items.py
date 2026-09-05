from column_of.column_of import column_of


def _needs(item: dict, graph: dict) -> list[str]:
    needs = list(item.get("needs", []))
    parent = graph.get(item.get("parent"))
    if item["kind"] == "test" and parent:
        needs = needs + parent.get("needs", [])
    return needs


def column_items(
    name: str, graph: dict, labels: dict[str, list[str]], config: dict
) -> list[dict]:
    if name not in config["columns"]:
        raise ValueError(f"not a column: {name}")
    filtered = config["columns"][name]["tier"] != "none"
    items = []
    for item_id, item in graph.items():
        if column_of(item, labels.get(item_id, []), config) != name:
            continue
        if filtered and any(
            graph.get(need, {}).get("state") != "done" for need in _needs(item, graph)
        ):
            continue
        items.append(item)
    return sorted(items, key=lambda i: i["id"])
