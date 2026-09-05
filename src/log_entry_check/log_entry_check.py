_REQUIRED_KEYS = {
    "item",
    "gate",
    "rule",
    "inputs",
    "state",
    "tokens",
    "seconds",
    "actor",
}


def log_entry_check(entry: dict) -> None:
    if set(entry.keys()) != _REQUIRED_KEYS:
        raise ValueError(
            "entry must contain exactly the keys: "
            "item, gate, rule, inputs, state, tokens, seconds, actor"
        )
    if not isinstance(entry["tokens"], int) or isinstance(entry["tokens"], bool):
        raise ValueError("tokens must be an int")
    if entry["seconds"] < 0:
        raise ValueError("seconds must be >= 0")
    if not entry["actor"]:
        raise ValueError("actor must be non-empty")
