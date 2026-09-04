from record_run.record_run import RecordError, record_run
from record_set_owner.record_set_owner import record_set_owner
from record_set_state.record_set_state import record_set_state


def claim_item(item_id: str, owner: str) -> dict:
    if not owner:
        raise ValueError("owner must not be empty")

    try:
        record_run(["update", item_id, "--claim"])
    except RecordError as exc:
        raise RecordError(
            "item is already claimed by someone else", exc.stderr
        ) from exc

    record_set_owner(item_id, owner)
    record_set_state(item_id, "in_progress")

    return {"id": item_id, "owner": owner, "state": "in_progress"}
