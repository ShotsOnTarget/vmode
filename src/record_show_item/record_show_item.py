from record_run.record_run import record_run, RecordError


def record_show_item(item_id: str) -> dict:
    items = record_run(["show", item_id])
    item = items[0]

    kind = ""
    state = ""
    for label in item.get("labels", []):
        if not kind and label.startswith("kind:"):
            kind = label[len("kind:"):]
        if not state and label.startswith("state:"):
            state = label[len("state:"):]

    return {
        "id": item.get("id", ""),
        "kind": kind,
        "title": item.get("title", ""),
        "owner": item.get("assignee", ""),
        "state": state,
        "parent": item.get("parent"),
        "sheet": item.get("description") or "",
    }
