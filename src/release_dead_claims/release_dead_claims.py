from datetime import UTC, datetime

from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state


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


def _release(item_id: str, state: str) -> None:
    record_run(["update", item_id, "-a", ""])
    if state == "in_progress":
        record_set_state(item_id, "ready")


def release_dead_claims(
    graph: dict, alive: set[str], timeout_seconds: int = 1800, now: str | None = None
) -> list[str]:
    """Release claims held by a dead or stalled puller.

    A claimed_by is a puller claim only when the text after its final dash
    is a pid (all digits); a person claim, an empty claim, and an item with
    no claim are left alone. A puller claim is released when its pid is not
    in alive, or when now minus the item's updated_at exceeds
    timeout_seconds, whatever state the item is in. Releasing empties the
    claim slot and, only when the item's state was in_progress, moves the
    item back to ready; any other state is kept. Side effects: reads each
    released item's updated_at and writes the release through the record.
    Returns the ids released, in graph order.
    """
    current = _parse(now) if now else datetime.now(UTC)
    released = []
    for item_id, item in graph.items():
        pid = _puller_pid(item.get("claimed_by") or "")
        if pid is None:
            continue
        if pid in alive and not _stale(item_id, timeout_seconds, current):
            continue
        _release(item_id, item["state"])
        released.append(item_id)
    return released
