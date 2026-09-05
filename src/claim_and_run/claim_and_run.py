import json
import os

from claim_item.claim_item import claim_item
from record_add_note.record_add_note import record_add_note
from record_run.record_run import RecordError, record_run
from record_set_state.record_set_state import record_set_state


def claim_and_run(item: dict, column: str, role: str, options: dict) -> bool:
    """Claim an item and run invoke on it, handling the checking/label/release
    transitions.
    """
    item_id = item["id"]
    prior_state = item["state"]
    try:
        claim_item(item_id, role + "-" + str(os.getpid()))
    except RecordError:
        return False
    try:
        usage = options["invoke"](item, column)
    except Exception as exc:
        record_run(["update", item_id, "-a", ""])
        record_set_state(item_id, "ready")
        record_add_note(item_id, "release: " + str(exc)[:200])
        return True
    record_add_note(item_id, "usage: " + json.dumps(usage))
    absent = options["config"]["columns"][column].get("labels_absent")
    if absent:
        record_run(["label", "add", item_id, absent[0]])
        record_run(["update", item_id, "-a", ""])
        record_set_state(item_id, prior_state)
    else:
        record_set_state(item_id, "checking")
    return True
