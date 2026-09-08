from record_graph.record_graph import record_graph
from record_run.record_run import record_run

_ACTIVE = "state:in_progress"


def _rows_for(kind: str, states: list[str]) -> list:
    wanted = {f"state:{state}" for state in states} | {_ACTIVE}
    return record_run(
        [
            "list",
            "--all",
            "-n",
            "0",
            "-l",
            f"kind:{kind}",
            "--label-any",
            ",".join(sorted(wanted)),
        ]
    )


def _needed_ids(rows: list, have: set) -> list:
    ids = set()
    for row in rows:
        for dep in row.get("dependencies", []):
            if dep.get("type") == "blocks":
                ids.add(dep["depends_on_id"])
    return sorted(ids - have)


def column_graph(column: str, config: dict) -> tuple[dict, dict]:
    """The record a puller needs to work one column, and nothing else.

    Inputs: column, a board column name; config, as board_config() returns.
    Outputs: (graph, labels) shaped exactly as record_graph() and
    record_labels() return them, holding only the rows that column can act
    on: its kinds in its own states, the same kinds in_progress so the WIP
    count is right, and the items those rows need first so a needs link can
    be resolved. Side effects: reads the record, one query per kind plus at
    most one more for the needed items. Raises ValueError for an unknown
    column.

    A whole-record read costs the same whether one item is waiting or a
    thousand are done, and nine items in ten are done. This asks for the
    handful a column could take, so the cost follows the work in flight
    rather than the history behind it.
    """
    if column not in config["columns"]:
        raise ValueError(f"not a column: {column}")
    rules = config["columns"][column]
    rows = []
    for kind in rules["kinds"]:
        rows.extend(_rows_for(kind, rules["states"]))
    by_id = {row["id"]: row for row in rows}
    missing = _needed_ids(rows, set(by_id))
    if missing:
        for row in record_run(["list", "--all", "-n", "0", "--id", ",".join(missing)]):
            by_id.setdefault(row["id"], row)
    items = list(by_id.values())
    return record_graph(items), {i["id"]: i.get("labels", []) for i in items}
