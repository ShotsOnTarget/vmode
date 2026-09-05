from record_run.record_run import record_run


def _label(labels, prefix):
    return next(
        (label.split(prefix, 1)[1] for label in labels if label.startswith(prefix)),
        "",
    )


def record_graph() -> dict[str, dict]:
    items = record_run(["list", "--all", "--exclude-type", "event"])

    graph = {}
    for item in items:
        item_id = item["id"]
        labels = item.get("labels", [])
        kind = _label(labels, "kind:")
        state = _label(labels, "state:")
        owner = _label(labels, "owner:")
        deps = item.get("dependencies", [])
        validates = [d["depends_on_id"] for d in deps if d.get("type") == "validates"]
        needs = [d["depends_on_id"] for d in deps if d.get("type") == "blocks"]
        parent = item.get("parent") or (validates[0] if validates else None)
        graph[item_id] = {
            "id": item_id,
            "kind": kind,
            "title": item.get("title", ""),
            "owner": owner,
            "state": state,
            "parent": parent,
            "checks": validates,
            "needs": needs,
            "claimed_by": item.get("assignee") or "",
        }

    return graph
