from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state


def release_dead_claims(graph: dict, alive: set[str]) -> list[str]:
    """Release every claim held by a puller that no longer exists.

    A claimant is 'role-<pid>'. When the pid is not in alive, the slot is
    cleared and an in_progress job goes back to ready so another puller can
    take it. Claims without a pid (a person's name) are left alone.
    Returns the ids released.
    """
    released = []
    for item_id, item in graph.items():
        claimant = item.get("claimed_by") or ""
        if "-" not in claimant or item["kind"] not in ("code", "test"):
            continue
        pid = claimant.rsplit("-", 1)[1]
        if not pid.isdigit() or pid in alive:
            continue
        record_run(["update", item_id, "-a", ""])
        if item["state"] == "in_progress":
            record_set_state(item_id, "ready")
        released.append(item_id)
    return released
