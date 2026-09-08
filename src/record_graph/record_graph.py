from record_run.record_run import record_run


def _label(labels, prefix):
    return next(
        (label.split(prefix, 1)[1] for label in labels if label.startswith(prefix)),
        "",
    )


def record_graph(items: list | None = None) -> dict[str, dict]:
    """Every non-event item as a dict: id, kind, title, owner, state, parent,
    checks (validates links), needs (blocks links), claimed_by.

    parent is the record's own parent field. Verification and validation
    items have none, so they fall back to the item they check; a test job
    hangs under its Story beside the code it checks, so no fallback.

    items: rows already fetched from the record, to shape without fetching
    again. Default None reads the whole record, which is what a caller that
    needs every item wants. column_graph passes the few rows one column can
    act on, so a puller shapes those and no others."""
    if items is None:
        items = record_run(["list", "--all", "--exclude-type", "event"])
    graph = {}
    for item in items:
        item_id = item["id"]
        labels = item.get("labels", [])
        kind = _label(labels, "kind:")
        deps = item.get("dependencies", [])
        validates = [d["depends_on_id"] for d in deps if d.get("type") == "validates"]
        needs = [d["depends_on_id"] for d in deps if d.get("type") == "blocks"]
        parent = item.get("parent")
        if not parent and validates and kind != "test":
            parent = validates[0]
        graph[item_id] = {
            "id": item_id,
            "kind": kind,
            "title": item.get("title", ""),
            "owner": _label(labels, "owner:"),
            "state": _label(labels, "state:"),
            "parent": parent,
            "checks": validates,
            "needs": needs,
            "claimed_by": item.get("assignee") or "",
        }
    return graph
