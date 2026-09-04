from record_run.record_run import record_run, RecordError


def record_set_owner(item_id: str, owner: str) -> dict:
    if not owner:
        raise ValueError("owner must not be empty")

    record_run(["update", item_id, "-a", owner])

    return {"id": item_id, "owner": owner}
