from raise_note.raise_note import raise_note
from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

_REQUIRED = ("action", "state", "retries", "rules")


def _release(job_id):
    record_run(["update", job_id, "-a", ""])


def _bounce(job_id, outcome):
    _release(job_id)
    record_add_note(job_id, "bounce: " + ",".join(outcome["rules"]))
    for label in record_run(["label", "list", job_id]):
        name = label if isinstance(label, str) else label.get("name", "")
        if name.startswith("retry:"):
            record_run(["label", "remove", job_id, name])
    record_run(["label", "add", job_id, f"retry:{outcome['retries']}"])
    raise_note(job_id, outcome)


def _escalate(job_id, outcome):
    _release(job_id)
    raise_note(job_id, outcome)


def prove_move(job_id: str, outcome: dict) -> None:
    for key in _REQUIRED:
        if key not in outcome:
            raise ValueError(f"outcome missing key: {key}")
    action = outcome["action"]
    if action == "bounce":
        _bounce(job_id, outcome)
    elif action == "escalate":
        _escalate(job_id, outcome)
    record_set_state(job_id, outcome["state"])
