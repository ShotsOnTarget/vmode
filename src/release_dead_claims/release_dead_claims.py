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
    """Release claims nobody can vouch for.

    claimed_by is either empty (no claim), a person such as architect whose
    name carries no pid, or a puller 'role-<pid>'. An empty claim is never
    touched. alive is the set of running puller pids; an empty alive set is
    an unavailable process listing, never proof that every puller is dead,
    so while it is empty no claim is released for being unlisted. A claim
    is stale when the item's updated_at is older than timeout_seconds; now
    defaults to the current UTC time when it is not given. A puller claim
    whose pid is missing from a non-empty alive set is released at once; a
    stale claim is released whether it is a puller's or a person's.
    Releasing empties the claim slot and, only
    when the item's state was in_progress, moves the item back to ready;
    any other state is kept. Side effects: reads each released item's
    updated_at and writes the release through the record. Returns the ids
    released, in graph order.
    """
    current = _parse(now) if now else datetime.now(UTC)
    released = []
    for item_id, item in graph.items():
        claimed_by = item.get("claimed_by") or ""
        if not claimed_by:
            continue
        pid = _puller_pid(claimed_by)
        dead = pid is not None and alive and pid not in alive
        stale = current is not None and _stale(item_id, timeout_seconds, current)
        if not dead and not stale:
            continue
        _release(item_id, item["state"])
        released.append(item_id)
    return released
