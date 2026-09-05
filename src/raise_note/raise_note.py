import os
import tempfile

from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run

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


def raise_note(job_id: str, outcome: dict) -> str:
    action, rules = outcome["action"], outcome["rules"]
    if action not in _ACTIONS:
        raise ValueError(f"action must be one of {_ACTIONS}, got {action!r}")

    title = f"{action}: {','.join(rules)}"[:80]
    note = record_create_item("note", title, "supervisor", parent=job_id)
    note_id = note["id"]

    lines = _summary_lines(job_id, action, outcome["retries"], rules)
    fd, path = tempfile.mkstemp(suffix=".md")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(lines) + "\n")
        record_run(["update", note_id, "--body-file", path])
    finally:
        os.remove(path)

    return note_id
