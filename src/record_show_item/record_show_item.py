from record_run.record_run import record_run


def record_show_item(item_id: str) -> dict:
    items = record_run(["show", item_id])
    item = items[0]

    kind = ""
    state = ""
    owner = ""
    for label in item.get("labels", []):
        if not kind and label.startswith("kind:"):
            kind = label[len("kind:") :]
        if not state and label.startswith("state:"):
            state = label[len("state:") :]
        if not owner and label.startswith("owner:"):
            owner = label[len("owner:") :]

    return {
        "id": item.get("id", ""),
        "kind": kind,
        "title": item.get("title", ""),
        "owner": owner,
        "state": state,
        "parent": item.get("parent"),
        "sheet": item.get("description") or "",
    }
