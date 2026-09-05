from column_of.column_of import column_of


def _needs(item: dict, graph: dict) -> list[str]:
    needs = list(item.get("needs", []))
    parent = graph.get(item.get("parent"))
    if item["kind"] == "test" and parent:
        needs = needs + parent.get("needs", [])
    return needs


def _waiting_on_code(item: dict, graph: dict) -> bool:
    if item["kind"] != "test" or item["state"] != "checking":
        return False
    parent = graph.get(item.get("parent"))
    return bool(parent) and parent["state"] != "done"


def _needs_unmet(item: dict, graph: dict) -> bool:
    return any(
        graph.get(need, {}).get("state") != "done" for need in _needs(item, graph)
    )


def column_items(
    name: str, graph: dict, labels: dict[str, list[str]], config: dict
) -> list[dict]:
    if name not in config["columns"]:
        raise ValueError(f"not a column: {name}")
    filtered = config["columns"][name]["tier"] != "none"

    def _excluded(item_id: str, item: dict) -> bool:
        if column_of(item, labels.get(item_id, []), config) != name:
            return True
        if _waiting_on_code(item, graph):
            return True
        return filtered and _needs_unmet(item, graph)

    items = [item for item_id, item in graph.items() if not _excluded(item_id, item)]
    return sorted(items, key=lambda i: i["id"])
