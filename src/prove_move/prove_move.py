import os

from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

_REQUIRED = ("action", "state", "retries", "rules")


def _bounce(job_id, rules, retries):
    record_add_note(job_id, "bounce: " + ",".join(rules))
    for label in record_run(["label", "list", job_id]):
        name = label if isinstance(label, str) else label.get("name", "")
        if name.startswith("retry:"):
            record_run(["label", "remove", job_id, name])
    record_run(["label", "add", job_id, f"retry:{retries}"])


def _escalate(job_id, rules, retries):
    lines = [
        f"- **Work item id**: {job_id}",
        "- **From**: Supervisor",
        "- **What failed**: gate checks did not pass.",
        f"- **How many times**: {retries}",
        f"- **Which rule or gate**: {', '.join(rules)}",
        f"- **What was already tried**: bounced {retries} time(s).",
        "- **Decision needed**: Architect: split, rewrite the sheet, or "
        "change the Story checklist",
    ]
    os.makedirs("work/summaries", exist_ok=True)
    with open(f"work/summaries/{job_id}.md", "w") as f:
        f.write("# Escalation summary\n\n" + "\n".join(lines) + "\n")


def prove_move(job_id: str, outcome: dict) -> None:
    for key in _REQUIRED:
        if key not in outcome:
            raise ValueError(f"outcome missing key: {key}")
    action, retries, rules = outcome["action"], outcome["retries"], outcome["rules"]
    if action == "bounce":
        _bounce(job_id, rules, retries)
    elif action == "escalate":
        _escalate(job_id, rules, retries)
    record_set_state(job_id, outcome["state"])
