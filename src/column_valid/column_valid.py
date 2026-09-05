_LEFT = {"intent", "story", "code", "proposal", "note"}
KINDS = _LEFT | {"test", "verification", "validation"}
STATES = {"waiting", "ready", "in_progress", "blocked", "checking", "done", "reopened"}
TIERS = {"human", "frontier", "cheap", "none"}
REQUIRED = {"kinds", "states", "role", "tier", "wip", "poll_seconds"}
ALLOWED = REQUIRED | {"labels_absent"}


def _is_kind_list(value):
    return isinstance(value, list) and bool(value) and set(value) <= KINDS


def _is_state_list(value):
    return isinstance(value, list) and bool(value) and set(value) <= STATES


def _is_int_at_least(value, minimum):
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _is_str_list(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


CHECKERS = (
    ("kinds", _is_kind_list, "must be a non-empty list of allowed kinds"),
    ("states", _is_state_list, "must be a non-empty list of allowed states"),
    ("role", lambda v: isinstance(v, str), "must be a str"),
    ("tier", lambda v: v in TIERS, "must be one of human, frontier, cheap, none"),
    ("wip", lambda v: _is_int_at_least(v, 0), "must be an int >= 0"),
    ("poll_seconds", lambda v: _is_int_at_least(v, 0), "must be an int >= 0"),
    ("labels_absent", _is_str_list, "must be a list of str"),
)


def column_valid(name: str, column: dict) -> list[str]:
    """Validate one column table from the TOML config and list its problems."""
    missing = [
        f"{f}: required key missing in '{name}'" for f in REQUIRED if f not in column
    ]
    extra = [f"{k}: unexpected key in '{name}'" for k in column if k not in ALLOWED]
    invalid = [
        f"{field}: {reason}"
        for field, is_valid, reason in CHECKERS
        if field in column and not is_valid(column[field])
    ]
    return missing + extra + invalid
