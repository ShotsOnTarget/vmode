def _rows(db: dict, item_id: str, side: str, other: str) -> list[dict]:
    items = db["items"]
    return [
        {**items[d[other]], "dependency_type": d["type"]}
        for d in db["deps"]
        if d[side] == item_id and d[other] in items
    ]


def fake_show(item_id: str, db: dict) -> list[dict]:
    """`bd show <id>` for the fake record: [item] with dependencies (each the
    depended-on item plus dependency_type), dependents, comments, parent."""
    if item_id not in db["items"]:
        raise LookupError(item_id)
    item = dict(db["items"][item_id])
    item["dependencies"] = _rows(db, item_id, "issue_id", "depends_on_id")
    item["dependents"] = _rows(db, item_id, "depends_on_id", "issue_id")
    item["comments"] = list(db["comments"].get(item_id, []))
    return [item]
