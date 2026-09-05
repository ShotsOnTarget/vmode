from record_run.record_run import record_run

_VALID_STATES = {
    "waiting",
    "ready",
    "in_progress",
    "blocked",
    "checking",
    "done",
    "reopened",
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


def _check_ready(item_id: str, labels: list[str]) -> None:
    """A Story is Ready only when its checklist (acceptance) is written."""
    if "kind:story" not in labels:
        return
    row = record_run(["show", item_id])[0]
    if not (row.get("acceptance_criteria") or "").strip():
        raise ValueError(f"story has no checklist: {item_id}")


def record_set_state(item_id: str, state: str) -> dict:
    if state not in _VALID_STATES:
        raise ValueError(f"invalid state: {state}")
    labels = record_run(["label", "list", item_id])
    labels = [x if isinstance(x, str) else x.get("name", "") for x in labels]
    if state == "ready":
        _check_ready(item_id, labels)
    for name in labels:
        if name.startswith("state:"):
            record_run(["label", "remove", item_id, name])
    record_run(["label", "add", item_id, f"state:{state}"])
    record_run(["update", item_id, "-s", _STATUS_MAP[state]])
    return {"id": item_id, "state": state}
