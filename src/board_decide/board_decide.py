from record_add_note.record_add_note import record_add_note
from record_graph.record_graph import record_graph
from record_set_owner.record_set_owner import record_set_owner
from record_set_state.record_set_state import record_set_state


def board_decide(intent_id: str, decision: str, reason: str) -> dict:
    if decision not in ("yes", "no"):
        raise ValueError(f"invalid decision: {decision}")
    if decision == "no" and not reason:
        raise ValueError("reason must not be empty for no")

    graph = record_graph()
    validation_id = next(
        (
            item_id
            for item_id, item in graph.items()
            if item.get("kind") == "validation" and intent_id in item.get("checks", [])
        ),
        None,
    )
    if validation_id is None:
        raise ValueError(f"no validation item checks intent: {intent_id}")

    state = "done" if decision == "yes" else "reopened"
    record_set_state(validation_id, state)
    record_set_owner(validation_id, "board")
    record_set_state(intent_id, state)

    note = "board: yes" if decision == "yes" else f"board: no: {reason}"
    record_add_note(validation_id, note)

    return {"intent": intent_id, "validation": validation_id, "state": state}
