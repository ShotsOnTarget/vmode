from record_add_note.record_add_note import record_add_note
from record_create_item.record_create_item import record_create_item
from record_run.record_run import RecordError, record_run
from record_set_state.record_set_state import record_set_state

STRIKES = 3
_FOR = (
    "For: architect. This item was released {n} times in a row without a run "
    "finishing, so it is blocked instead of going round again. The release "
    "comments on it hold each reason; the last one is: {reason}"
)


def _comments(item_id: str) -> list:
    try:
        return record_run(["comments", item_id])
    except RecordError:
        return record_run(["show", item_id])[0].get("comments", [])


def _strikes(item_id: str) -> int:
    """Releases since the last finished run: newest first, stop at usage:."""
    count = 0
    for comment in reversed(_comments(item_id)):
        text = comment.get("text", "")
        if text.startswith("usage:"):
            break
        if text.startswith("release:"):
            count += 1
    return count


def release_strike(item_id: str, prior_state: str, reason: str) -> str:
    """Count a run that ended with no result and put the item where it belongs.

    Inputs: item_id; prior_state, the state the item held before the claim;
    reason, the error text. A release is not a bounce: no gate judged the
    work, so the item normally returns to prior_state for another try. The
    count is the run of release: comments since the last usage: comment, so
    a finished run resets it. On the third release in a row the item is set
    blocked instead and a note item under it, owned by the architect and
    addressed to the Architect, says why, so a run that can never finish
    stops looping unseen. Outputs: the state set, prior_state or 'blocked'.
    Side effects: one release: comment (reason kept to 1000 characters), the
    state, and on the third strike one note item with its own comment.
    """
    strikes = _strikes(item_id) + 1
    record_add_note(item_id, "release: " + reason[:1000])
    if strikes < STRIKES:
        record_set_state(item_id, prior_state)
        return prior_state
    record_set_state(item_id, "blocked")
    title = f"released {strikes} times: {reason[:50]}"
    note = record_create_item("note", title, "architect", item_id)
    record_add_note(note["id"], _FOR.format(n=strikes, reason=reason[:300]))
    return "blocked"
