from log_read_item.log_read_item import log_read_item

_ACTIONS = {"log_done": "gate_pass", "bounce": "gate_fail", "escalate": "gate_fail"}


def _transition(entry: dict) -> tuple[str, str] | None:
    inputs = entry.get("inputs") or {}
    action = inputs.get("action") if isinstance(inputs, dict) else None
    if action in _ACTIONS:
        return ("checking", _ACTIONS[action])
    ready = entry.get("gate") == "ready" and entry["state"] in ("waiting", "ready")
    edited = entry["state"] == "reopened"
    return (
        ("done", "edited")
        if edited
        else (("waiting", "ready_gate_pass") if ready else None)
    )


def log_events(item_id: str) -> list[tuple[str, str]]:
    """(from_state, event) transitions for one item, read from its events.

    Gate events carry inputs.action (log_done, bounce, escalate), which map
    to gate_pass and gate_fail from checking; a reopened state is edited from
    done; a ready gate on a waiting item is ready_gate_pass. Other events
    (lessons, corrections, Board notes) produce no transition.
    """
    results = []
    for entry in log_read_item(item_id):
        if "state" not in entry:
            raise ValueError(f"entry missing state: {entry}")
        transition = _transition(entry)
        if transition:
            results.append(transition)
    return results
