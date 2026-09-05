from column_of.column_of import column_of


def _needs_unmet(item: dict, graph: dict) -> bool:
    needs = item.get("needs", [])
    return any(graph.get(need, {}).get("state") != "done" for need in needs)


def column_items(
    name: str, graph: dict, labels: dict[str, list[str]], config: dict
) -> list[dict]:
    """Items a puller may take from one column, sorted by id.

    An item is listed when column_of places it in the column and, for a
    pulling column (tier not 'none'), every item it needs is done. Gating
    columns list everything in their states: needs gate pulling, never
    gating. Ordering between code and test is a needs link, nothing more.
    """
    if name not in config["columns"]:
        raise ValueError(f"not a column: {name}")
    filtered = config["columns"][name]["tier"] != "none"
    items = [
        item
        for item_id, item in graph.items()
        if column_of(item, labels.get(item_id, []), config) == name
        and not (filtered and _needs_unmet(item, graph))
    ]
    return sorted(items, key=lambda i: i["id"])
