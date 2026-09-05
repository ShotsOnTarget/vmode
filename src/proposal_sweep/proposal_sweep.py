from proposal_check.proposal_check import proposal_check
from record_add_note.record_add_note import record_add_note
from record_set_state.record_set_state import record_set_state
from record_show_item.record_show_item import record_show_item

_OPEN = ("waiting", "ready", "blocked")


def _gate(item_id: str, state: str) -> bool:
    problems = proposal_check(record_show_item(item_id))
    if not problems:
        record_set_state(item_id, "checking")
        return True
    if state != "blocked":
        record_add_note(item_id, "proposal gate: " + ", ".join(problems))
        record_set_state(item_id, "blocked")
    return False


def proposal_sweep(graph: dict) -> list[str]:
    """Move every waiting proposal through the proposal gate.

    A proposal whose sheet passes proposal_check goes to checking, which is
    the Board's validate column, where Yes applies it and No reopens it. A
    proposal that fails is blocked with a comment naming the rules, so its
    author sees why; a blocked one is re-checked every pass, so a sheet
    finished after the first gate gets through. Returns the ids moved.
    """
    open_ones = (
        (i, v["state"])
        for i, v in graph.items()
        if v["kind"] == "proposal" and v["state"] in _OPEN
    )
    return [item_id for item_id, state in open_ones if _gate(item_id, state)]
