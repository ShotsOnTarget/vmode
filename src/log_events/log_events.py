from log_read_item.log_read_item import log_read_item

_RULES = (
    (lambda s, r: s == "done", "checking", "gate_pass"),
    (
        lambda s, r: s in ("in_progress", "ready") and "retry" in r.get("inputs", ""),
        "checking",
        "gate_fail",
    ),
    (lambda s, r: s == "blocked", "checking", "gate_fail"),
    (lambda s, r: s == "reopened", "done", "edited"),
    (
        lambda s, r: s in ("waiting", "ready") and r.get("gate") == "Ready",
        "waiting",
        "ready_gate_pass",
    ),
)


def log_events(path: str, item_id: str) -> list[tuple[str, str]]:
    """Derive (from_state, event) transitions for one item from a JSON-lines log."""
    results = []
    for entry in log_read_item(path, item_id):
        if "state" not in entry:
            raise ValueError(f"entry missing state: {entry}")
        state = entry["state"]
        for predicate, from_state, event in _RULES:
            if predicate(state, entry):
                results.append((from_state, event))
                break
    return results
