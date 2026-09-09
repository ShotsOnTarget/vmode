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


def _swap(labels: list[str], state: str) -> list[str]:
    """The label flags that take the old state off and put the new one on."""
    wanted = f"state:{state}"
    args = []
    for name in labels:
        if name.startswith("state:") and name != wanted:
            args += ["--remove-label", name]
    if wanted not in labels:
        args += ["--add-label", wanted]
    return args


def record_set_state(item_id: str, state: str) -> dict:
    """Set an item's workflow state label and matching bd status in one write.

    The old state label comes off and the new one goes on in the same
    `update` call as the status, so a write that fails leaves the old state
    rather than none (five items lost their label mid-swap on 2026-09-09
    and vanished from every column). Setting reopened also clears the claim
    slot, so any builder may take the job again.
    """
    if state not in _VALID_STATES:
        raise ValueError(f"invalid state: {state}")
    labels = record_run(["label", "list", item_id])
    labels = [x if isinstance(x, str) else x.get("name", "") for x in labels]
    if state == "ready":
        _check_ready(item_id, labels)
    args = ["update", item_id, *_swap(labels, state), "-s", _STATUS_MAP[state]]
    if state == "reopened":
        args += ["-a", ""]
    record_run(args)
    return {"id": item_id, "state": state}
