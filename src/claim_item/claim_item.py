from record_run.record_run import RecordError, record_run
from record_set_state.record_set_state import record_set_state


def claim_item(item_id: str, actor: str) -> dict:
    if not actor:
        raise ValueError("actor must not be empty")

    try:
        record_run(["update", item_id, "--claim", "--actor", actor])
    except RecordError as exc:
        raise RecordError("issue already claimed by another actor", exc.stderr) from exc

    record_set_state(item_id, "in_progress")

    return {"id": item_id, "claimed_by": actor, "state": "in_progress"}
