from record_run.record_run import record_run


def record_graph() -> dict[str, dict]:
    items = record_run(["list", "--all"])

    graph = {}
    for item in items:
        item_id = item["id"]
        labels = item.get("labels", [])
        kind = next(
            (
                label.split("kind:", 1)[1]
                for label in labels
                if label.startswith("kind:")
            ),
            "",
        )
        state = next(
            (
                label.split("state:", 1)[1]
                for label in labels
                if label.startswith("state:")
            ),
            "",
        )
        deps = item.get("dependencies", [])
        validates = [d["depends_on_id"] for d in deps if d.get("type") == "validates"]
        needs = [d["depends_on_id"] for d in deps if d.get("type") == "blocks"]
        parent = item.get("parent") or (validates[0] if validates else None)
        graph[item_id] = {
            "id": item_id,
            "kind": kind,
            "title": item.get("title", ""),
            "owner": item.get("owner", ""),
            "state": state,
            "parent": parent,
            "checks": validates,
            "needs": needs,
        }

    return graph
