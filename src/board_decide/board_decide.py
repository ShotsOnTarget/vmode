import datetime

from proposal_apply.proposal_apply import proposal_apply
from record_add_note.record_add_note import record_add_note
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from record_set_owner.record_set_owner import record_set_owner
from record_set_state.record_set_state import record_set_state


def _proposal(proposal_id: str, decision: str, reason: str) -> dict:
    """Yes applies the proposal's diff and closes it; No reopens it with the reason."""
    if decision == "yes":
        today = datetime.date.today().isoformat()
        return {**proposal_apply(proposal_id, ".", today), "state": "done"}
    record_set_state(proposal_id, "reopened")
    record_add_note(proposal_id, f"board: no: {reason}")
    return {"id": proposal_id, "state": "reopened"}


def _smoke_override(intent_id: str) -> str:
    """The Intent's latest smoke verdict, when it is failed or skipped, else empty."""
    shown = record_run(["show", intent_id])[0]
    for comment in reversed(shown.get("comments", [])):
        text = comment.get("text", "")
        if not text.startswith("smoke: "):
            continue
        verdict = text[len("smoke: ") :].split(" ", 1)[0]
        return verdict if verdict in ("failed", "skipped") else ""
    return ""


def _note(intent_id: str, decision: str, reason: str) -> str:
    """The board note; a yes that used failed or skipped smoke says so."""
    if decision == "no":
        return f"board: no: {reason}"
    verdict = _smoke_override(intent_id)
    return f"board: yes; smoke: {verdict}" if verdict else "board: yes"


def board_decide(intent_id: str, decision: str, reason: str) -> dict:
    """Record the Board's yes or no. For an Intent the validation item and the
    Intent move together; a yes over failed or skipped smoke evidence says so
    in its note. For a proposal, yes applies the diff (see _proposal).
    """
    if decision not in ("yes", "no"):
        raise ValueError(f"invalid decision: {decision}")
    if decision == "no" and not reason:
        raise ValueError("reason must not be empty for no")

    graph = record_graph()
    if graph.get(intent_id, {}).get("kind") == "proposal":
        return _proposal(intent_id, decision, reason)
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

    note = _note(intent_id, decision, reason)
    record_add_note(validation_id, note)

    return {"intent": intent_id, "validation": validation_id, "state": state}
