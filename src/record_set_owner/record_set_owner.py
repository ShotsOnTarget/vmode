from record_run.record_run import record_run


def record_set_owner(item_id: str, owner: str) -> dict:
    if not owner:
        raise ValueError("owner must not be empty")

    labels = record_run(["label", "list", item_id])
    for label in labels:
        if label.startswith("owner:"):
            record_run(["label", "remove", item_id, label])
    record_run(["label", "add", item_id, f"owner:{owner}"])

    return {"id": item_id, "owner": owner}
