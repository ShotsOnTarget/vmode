import tomllib

from column_valid.column_valid import column_valid


def _check_limits(limits):
    for key in ("max_parallel_model_runs", "claim_timeout_seconds"):
        value = limits.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"limits: invalid {key}")


def _check_conflicts(columns):
    names = list(columns)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            ca, cb = columns[a], columns[b]
            if (
                set(ca["kinds"]) & set(cb["kinds"])
                and set(ca["states"]) & set(cb["states"])
                and ca.get("labels_absent", []) == cb.get("labels_absent", [])
            ):
                raise ValueError(f"{a}/{b}: conflicting kinds and states")


def board_config(path: str) -> dict:
    """Parse and validate a board configuration TOML file.

    Input: path, the file system path of a board configuration TOML file.
    Output: the parsed TOML as a dict with the keys "columns" and "limits".
    Side effects: opens the file at path and reads nothing else.
    """
    with open(path, "rb") as handle:
        config = tomllib.load(handle)
    columns = config.get("columns", {})
    for name, column in columns.items():
        problems = column_valid(name, column)
        if problems:
            raise ValueError(f"{name}: {problems[0]}")
    _check_conflicts(columns)
    _check_limits(config.get("limits", {}))
    return config
