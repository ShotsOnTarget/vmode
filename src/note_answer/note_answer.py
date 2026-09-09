from record_add_note.record_add_note import record_add_note
from record_set_state.record_set_state import record_set_state
from record_show_item.record_show_item import record_show_item


def note_answer(note_id: str, role: str, text: str) -> dict:
    """Record one role's answer on a note it owns, or the Board's, and set it
    done; refuse anyone else with the name of the owner that owes the answer."""
    if not text:
        raise ValueError("text must not be empty")
    item = record_show_item(note_id)
    owner = item["owner"]
    if role not in ("board", owner):
        raise ValueError(f"{owner} owes the answer")
    record_add_note(note_id, f"answer ({role}): {text}")
    record_set_state(note_id, "done")
    return {"id": note_id, "role": role}
