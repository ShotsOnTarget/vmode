from board_config.board_config import board_config
from claim_and_run.claim_and_run import claim_and_run
from column_graph.column_graph import column_graph
from column_items.column_items import column_items
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from wip_headroom.wip_headroom import wip_headroom


def _global_headroom(graph: dict, config: dict) -> int:
    modelled = {
        kind
        for rules in config["columns"].values()
        if rules["tier"] not in ("none", "human")
        and rules["role"] != "none"
        and rules["poll_seconds"] > 0
        for kind in rules["kinds"]
        if kind != "intent"
    }
    busy = sum(
        item["state"] == "in_progress" and item["kind"] in modelled
        for item in graph.values()
    )
    return max(0, config["limits"]["max_parallel_model_runs"] - busy)


def _busy() -> dict:
    """Every item a model is working on right now, and nothing else.

    The spend cap counts claimed work, so this asks the record for exactly
    that rather than reading every item to count the few that are busy.
    """
    rows = record_run(
        [
            "list",
            "--all",
            "-n",
            "0",
            "--exclude-type",
            "event",
            "-l",
            "state:in_progress",
        ]
    )
    return record_graph(rows)


def _take(offers: list[dict], column: str, options: dict, headroom: int) -> list[str]:
    """Claim and run offers, skipping refused claims, until headroom is filled."""
    labels = options["labels"]
    claimed = []
    for item in offers:
        if len(claimed) >= headroom:
            break
        item = {**item, "labels": list(labels.get(item["id"], []))}
        if claim_and_run(item, column, options["role"], options):
            claimed.append(item["id"])
    return claimed


def pull_once(role: str, config_path: str, invoke) -> list[str]:
    """Pull ready items into a role's columns and invoke work on them.

    A refused claim (another actor holds it) costs only the offer it was
    made on, never the column's headroom; the pass moves to the next.
    """
    config = board_config(config_path)
    columns = [n for n, r in config["columns"].items() if r["role"] == role]
    if not columns:
        raise ValueError(f"no column for role: {role}")
    cap = _global_headroom(_busy(), config)
    options = {"config": config, "invoke": invoke, "role": role}
    claimed = []
    for column in columns:
        graph, labels = column_graph(column, config)
        headroom = min(wip_headroom(column, graph, config), cap - len(claimed))
        options["labels"] = labels
        offers = column_items(column, graph, labels, config)
        claimed.extend(_take(offers, column, options, headroom))
    return claimed
