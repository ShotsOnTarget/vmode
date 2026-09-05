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


_OPTIONAL_KEYS = {"usd", "turns"}


def _check_optional(entry: dict) -> None:
    usd, turns = entry.get("usd"), entry.get("turns")
    if usd is not None and (isinstance(usd, bool) or not isinstance(usd, int | float)):
        raise ValueError("usd must be a number or None")
    if turns is not None and (isinstance(turns, bool) or not isinstance(turns, int)):
        raise ValueError("turns must be an int or None")


def log_entry_check(entry: dict) -> None:
    """Validate a log entry before it is appended: exactly the required keys
    (item, gate, rule, inputs, state, tokens, seconds, actor), optionally usd
    (a number or None: the harness cost) and turns (an int or None)."""
    keys = set(entry.keys())
    if not keys >= _REQUIRED_KEYS or not keys <= _REQUIRED_KEYS | _OPTIONAL_KEYS:
        raise ValueError(
            "entry must contain exactly the keys: "
            "item, gate, rule, inputs, state, tokens, seconds, actor (and usd, turns)"
        )
    _check_optional(entry)
    if not isinstance(entry["tokens"], int) or isinstance(entry["tokens"], bool):
        raise ValueError("tokens must be an int")
    if entry["seconds"] < 0:
        raise ValueError("seconds must be >= 0")
    if not entry["actor"]:
        raise ValueError("actor must be non-empty")
