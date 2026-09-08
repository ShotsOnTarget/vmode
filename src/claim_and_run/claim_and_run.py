import json
import os

from claim_item.claim_item import claim_item
from last_gate.last_gate import last_gate
from record_add_note.record_add_note import record_add_note
from record_run.record_run import RecordError, record_run
from record_set_state.record_set_state import record_set_state
from release_strike.release_strike import release_strike


def _state(item_id: str) -> str:
    labels = record_run(["label", "list", item_id])
    names = [x if isinstance(x, str) else x.get("name", "") for x in labels]
    return next((n[6:] for n in names if n.startswith("state:")), "")


def _release(item_id: str, prior_state: str, exc: Exception) -> None:
    record_run(["update", item_id, "-a", ""])
    release_strike(item_id, prior_state, str(exc))


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


_REPORT = 4000  # a bd argument rides the Windows command line, capped near 32k


def _bounded(usage: dict) -> dict:
    report = str(usage.get("report") or "")
    if len(report) <= _REPORT:
        return usage
    tail = " ... (trimmed; the transcript holds the whole report)"
    return {**usage, "report": report[:_REPORT] + tail}


def _log(word: str, item_id: str, column: str) -> None:
    print(word + " " + item_id + " " + column, flush=True)


def claim_and_run(item: dict, column: str, role: str, options: dict) -> bool:
    """Claim an item and run invoke on it; False when another puller won the
    claim. The item handed to invoke carries last_gate: what the last gate
    or failed run said about it, so a retry knows what to fix. A failed run
    releases the item (see release_strike: back to its prior state, or
    blocked on the third release in a row); a finished run records usage,
    report cut to 4000 characters (a 34k report on one command line
    stranded a finished job, WinError 206, 2026-09-08), and moves the item
    on (see _finish). Prints 'claim <item id> <column>' once the claim is
    won and 'finish <item id> <column>' once the pass is over; a puller
    that took nothing prints nothing."""
    item_id = item["id"]
    try:
        claim_item(item_id, role + "-" + str(os.getpid()))
    except RecordError:
        return False
    _log("claim", item_id, column)
    try:
        usage = options["invoke"]({**item, "last_gate": last_gate(item_id)}, column)
    except Exception as exc:
        _release(item_id, item["state"], exc)
        _log("finish", item_id, column)
        return True
    record_add_note(item_id, "usage: " + json.dumps(_bounded(usage)))
    _finish(
        item_id,
        item["state"],
        options["config"]["columns"][column].get("labels_absent"),
    )
    _log("finish", item_id, column)
    return True
