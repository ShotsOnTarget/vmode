import json

from log_entry_check.log_entry_check import log_entry_check
from record_run.record_run import record_run


def log_append(entry: dict) -> str:
    """Record one event against a work item as an event bead: the gate, rule,
    inputs, state, tokens, seconds, and the harness cost (usd) and turns."""
    log_entry_check(entry)

    gate = entry["gate"]
    fields = ("rule", "inputs", "state", "tokens", "seconds")
    payload = {key: entry[key] for key in fields}
    payload.update(usd=entry.get("usd"), turns=entry.get("turns"))
    payload = json.dumps(payload, sort_keys=True)
    result = record_run(
        [
            "create",
            f"{gate}: {entry['rule'][:60]}",
            "--type",
            "event",
            "--event-actor",
            entry["actor"],
            "--event-category",
            gate.lower(),
            "--event-target",
            entry["item"],
            "--event-payload",
            payload,
        ]
    )
    return result["id"]
