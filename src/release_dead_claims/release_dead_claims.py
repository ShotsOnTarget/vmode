from datetime import UTC, datetime

from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

_RESET = {"code": "ready", "test": "ready", "note": "ready", "story": "done"}


def _parse(instant: str) -> datetime:
    return datetime.fromisoformat(instant.replace("Z", "+00:00"))


def _puller_pid(claimed_by: str) -> str | None:
    if "-" not in claimed_by:
        return None
    pid = claimed_by.rsplit("-", 1)[1]
    return pid if pid.isdigit() else None


def _stale(item_id: str, timeout_seconds: int, current: datetime) -> bool:
    updated = record_run(["show", item_id])[0]["updated_at"]
    return (current - _parse(updated)).total_seconds() > timeout_seconds


def _release(item_id: str, item: dict) -> None:
    record_run(["update", item_id, "-a", ""])
    if item["kind"] in _RESET:
        record_set_state(item_id, _RESET[item["kind"]])


def release_dead_claims(
    graph: dict, alive: set[str], timeout_seconds: int = 1800, now: str | None = None
) -> list[str]:
    """Release claims held by a dead or stalled puller.

    A candidate is an item whose state is in_progress and whose claimed_by
    is a puller claim 'role-<pid>'; a person's claim (no digits after the
    last dash) is left alone. A candidate is released when its pid is not
    in alive, or when now minus the item's updated_at exceeds
    timeout_seconds. Releasing empties the claim slot and moves a code,
    test or note back to ready and a story back to done; any other kind
    keeps its state. Every other item is untouched: no claim slot emptied,
    no state moved. Side effects: reads each candidate's updated_at and
    writes the release through the record.
    Returns the ids released, in graph order.
    """
    current = _parse(now) if now else datetime.now(UTC)
    released = []
    for item_id, item in graph.items():
        if item["state"] != "in_progress":
            continue
        pid = _puller_pid(item.get("claimed_by") or "")
        if pid is None:
            continue
        if pid in alive and not _stale(item_id, timeout_seconds, current):
            continue
        _release(item_id, item)
        released.append(item_id)
    return released
