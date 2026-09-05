from proposal_check.proposal_check import proposal_check
from record_add_note.record_add_note import record_add_note
from record_set_state.record_set_state import record_set_state
from record_show_item.record_show_item import record_show_item


def proposal_sweep(graph: dict) -> list[str]:
    """Move every waiting proposal through the proposal gate.

    A proposal whose sheet passes proposal_check goes to checking, which is
    the Board's validate column, where Yes applies it and No reopens it. A
    proposal that fails is blocked with a comment naming the rules, so its
    author sees why. Returns the ids moved to checking.
    """
    moved = []
    for item_id, item in graph.items():
        if item["kind"] != "proposal" or item["state"] not in ("waiting", "ready"):
            continue
        problems = proposal_check(record_show_item(item_id))
        if problems:
            record_add_note(item_id, "proposal gate: " + ", ".join(problems))
            record_set_state(item_id, "blocked")
        else:
            record_set_state(item_id, "checking")
            moved.append(item_id)
    return moved
