import json

_REQUIRED_KEYS = {"ts", "item", "gate", "rule", "inputs", "state", "tokens", "seconds"}


def log_append(path: str, entry: dict) -> None:
    if set(entry.keys()) != _REQUIRED_KEYS:
        raise ValueError("entry must contain exactly the keys: ts, item, gate, rule, inputs, state, tokens, seconds")
    if not isinstance(entry["tokens"], int) or isinstance(entry["tokens"], bool):
        raise ValueError("tokens must be an int")
    if entry["seconds"] < 0:
        raise ValueError("seconds must be >= 0")
    with open(path, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
