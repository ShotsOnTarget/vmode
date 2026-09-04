from column_of.column_of import column_of


def _empty_columns(config: dict) -> dict:
    return {
        name: {
            "name": name,
            "role": rules["role"],
            "wip": rules["wip"],
            "in_progress": 0,
            "items": [],
        }
        for name, rules in config["columns"].items()
    }


def board_columns(graph: dict, labels: dict, config: dict) -> list[dict]:
    columns = _empty_columns(config)
    for item_id, item in graph.items():
        name = column_of(item, labels.get(item_id, []), config)
        if name is None:
            continue
        fields = ("id", "kind", "title", "state")
        columns[name]["items"].append({field: item[field] for field in fields})
        if item["state"] == "in_progress":
            columns[name]["in_progress"] += 1
    for column in columns.values():
        column["items"].sort(key=lambda x: x["id"])
    return list(columns.values())
