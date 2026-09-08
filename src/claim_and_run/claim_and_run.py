import json
import os

from claim_item.claim_item import claim_item
from record_add_note.record_add_note import record_add_note
from record_run.record_run import RecordError, record_run
from record_set_state.record_set_state import record_set_state


def _state(item_id: str) -> str:
    labels = record_run(["label", "list", item_id])
    names = [x if isinstance(x, str) else x.get("name", "") for x in labels]
    return next((n[6:] for n in names if n.startswith("state:")), "")


def _release(item_id: str, prior_state: str, exc: Exception) -> None:
    record_run(["update", item_id, "-a", ""])
    record_set_state(item_id, prior_state)
    record_add_note(item_id, "release: " + str(exc)[:200])


def _finish(item_id: str, prior_state: str, absent: list | None) -> None:
    """After a run: a label column adds its label and clears the claim, keeping
    a state the role set; any other column moves the item to checking."""
    if not absent:
        record_set_state(item_id, "checking")
        return
    record_run(["label", "add", item_id, absent[0]])
    record_run(["update", item_id, "-a", ""])
    if _state(item_id) == "in_progress":  # the role left the state alone
        record_set_state(item_id, prior_state)


def _log(word: str, item_id: str, column: str) -> None:
    print(word + " " + item_id + " " + column, flush=True)


def claim_and_run(item: dict, column: str, role: str, options: dict) -> bool:
    """Claim an item and run invoke on it; False when another puller won the
    claim. A failed run releases the item back to the state it held before
    the claim with the error noted; a finished run records usage and moves
    the item on (see _finish). Prints 'claim <item id> <column>' once the
    claim is won and 'finish <item id> <column>' once the pass is over; a
    puller that took nothing prints nothing."""
    item_id = item["id"]
    try:
        claim_item(item_id, role + "-" + str(os.getpid()))
    except RecordError:
        return False
    _log("claim", item_id, column)
    try:
        usage = options["invoke"](item, column)
    except Exception as exc:
        _release(item_id, item["state"], exc)
        _log("finish", item_id, column)
        return True
    record_add_note(item_id, "usage: " + json.dumps(usage))
    _finish(
        item_id,
        item["state"],
        options["config"]["columns"][column].get("labels_absent"),
    )
    _log("finish", item_id, column)
    return True
