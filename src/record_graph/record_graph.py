from record_run.record_run import record_run, RecordError


def record_graph() -> dict[str, dict]:
    items = record_run(["list", "--all"])

    graph = {}
    for item in items:
        item_id = item["id"]
        labels = item.get("labels", [])
        kind = next(
            (l.split("kind:", 1)[1] for l in labels if l.startswith("kind:")), ""
        )
        state = next(
            (l.split("state:", 1)[1] for l in labels if l.startswith("state:")), ""
        )
        deps = item.get("dependencies", [])
        checks = [
            d["depends_on_id"] for d in deps if d.get("type") == "validates"
        ]
        needs = [
            d["depends_on_id"] for d in deps if d.get("type") == "blocks"
        ]
        graph[item_id] = {
            "id": item_id,
            "kind": kind,
            "title": item.get("title", ""),
            "owner": item.get("owner", ""),
            "state": state,
            "parent": item.get("parent"),
            "checks": checks,
            "needs": needs,
        }

    return graph
