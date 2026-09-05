import json

from log_append.log_append import log_append


def log_migrate(path: str) -> int:
    """Replay an old JSON-lines gate log into the record as event beads."""
    with open(path) as f:
        raw_lines = f.readlines()

    count = 0
    for raw_line in raw_lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed line: {raw_line}") from exc
        required = {"ts", "item", "gate", "rule", "inputs", "state"}
        if not required.issubset(record):
            raise ValueError(f"missing required keys: {raw_line}")

        inputs = dict(record["inputs"])
        inputs["ts_original"] = record["ts"]
        actor = inputs.get("actor", "migrated")
        log_append(
            {
                "item": record["item"],
                "gate": record["gate"],
                "rule": record["rule"],
                "inputs": inputs,
                "state": record["state"],
                "tokens": record.get("tokens", -1),
                "seconds": record.get("seconds", 0.0),
                "actor": actor,
            }
        )
        count += 1

    return count
