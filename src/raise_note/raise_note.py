import os
import tempfile

from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run
from summary_lines.summary_lines import summary_lines

_ACTIONS = ("bounce", "escalate")


def _summary_lines(job_id: str, action: str, retries: int, rules: list) -> list:
    return [
        f"- **Work item id**: {job_id}",
        "- **From**: Supervisor",
        "- **What failed**: gate checks did not pass.",
        f"- **How many times**: {retries}",
        f"- **Which rule or gate**: {', '.join(rules)}",
        f"- **What was already tried**: {action}d {retries} time(s).",
        "- **Decision needed**: Architect: split, rewrite the sheet, or "
        "change the Story checklist",
    ]


def _note_parts(job_id: str, outcome: dict, action: str, rules: list) -> tuple:
    recipient = outcome.get("recipient")
    if recipient:
        return recipient, summary_lines(job_id, outcome, recipient)
    return "supervisor", _summary_lines(job_id, action, outcome["retries"], rules)


def raise_note(job_id: str, outcome: dict) -> str:
    """Create a note item under a job, with the escalation summary as its description,
    for a bounce or an escalate. When outcome has a non-empty `recipient`, the note is
    owned by that role and its description is the eight summary_lines for it; otherwise
    the note is the Supervisor's and the description has no For line.
    """
    action, rules = outcome["action"], outcome["rules"]
    if action not in _ACTIONS:
        raise ValueError(f"action must be one of {_ACTIONS}, got {action!r}")

    owner, lines = _note_parts(job_id, outcome, action, rules)
    note = record_create_item(
        "note", f"{action}: {','.join(rules)}"[:80], owner, parent=job_id
    )
    note_id = note["id"]

    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(lines) + "\n")
        record_run(["update", note_id, "--body-file", path])
    finally:
        os.remove(path)

    return note_id
