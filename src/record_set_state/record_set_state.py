from record_run.record_run import record_run, RecordError

_VALID_STATES = {
    "waiting", "ready", "in_progress", "blocked",
    "checking", "done", "reopened",
}

_STATUS_MAP = {
    "waiting": "open",
    "ready": "open",
    "checking": "open",
    "reopened": "open",
    "in_progress": "in_progress",
    "blocked": "blocked",
    "done": "closed",
}


def record_set_state(item_id: str, state: str) -> dict:
    if state not in _VALID_STATES:
        raise ValueError(f"invalid state: {state}")

    labels = record_run(["label", "list", item_id])
    for label in labels:
        name = label if isinstance(label, str) else label.get("name", "")
        if name.startswith("state:"):
            record_run(["label", "remove", item_id, name])

    record_run(["label", "add", item_id, f"state:{state}"])
    record_run(["update", item_id, "-s", _STATUS_MAP[state]])

    return {"id": item_id, "state": state}
