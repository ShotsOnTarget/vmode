import json

_REQUIRED_KEYS = {"ts", "item", "gate", "rule", "inputs", "state"}


def log_append(path: str, entry: dict) -> None:
    if set(entry.keys()) != _REQUIRED_KEYS:
        raise ValueError("entry must contain exactly the keys: ts, item, gate, rule, inputs, state")
    with open(path, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
