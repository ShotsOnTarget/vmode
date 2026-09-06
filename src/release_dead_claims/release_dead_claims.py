from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

_RESET = {"code": "ready", "test": "ready", "note": "ready", "story": "done"}


def release_dead_claims(graph: dict, alive: set[str]) -> list[str]:
    """Release every claim held by a puller that no longer exists.

    A claimant is 'role-<pid>'. When the pid is not in alive, the slot is
    cleared, whatever the kind; an in_progress job or note goes back to
    ready and a Story back to done, so another puller can take it. Claims
    without a pid (a person's name) are left alone.
    Returns the ids released.
    """
    released = []
    for item_id, item in graph.items():
        claimant = item.get("claimed_by") or ""
        if "-" not in claimant:
            continue
        pid = claimant.rsplit("-", 1)[1]
        if not pid.isdigit() or pid in alive:
            continue
        record_run(["update", item_id, "-a", ""])
        if item["state"] == "in_progress" and item["kind"] in _RESET:
            record_set_state(item_id, _RESET[item["kind"]])
        released.append(item_id)
    return released
