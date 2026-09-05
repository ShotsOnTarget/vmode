from board_config.board_config import board_config
from claim_and_run.claim_and_run import claim_and_run
from column_items.column_items import column_items
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from wip_headroom.wip_headroom import wip_headroom


def _global_headroom(graph: dict, config: dict) -> int:
    modelled = {
        kind
        for rules in config["columns"].values()
        if rules["tier"] not in ("none", "human")
        for kind in rules["kinds"]
    }
    busy = sum(
        item["state"] == "in_progress" and item["kind"] in modelled
        for item in graph.values()
    )
    return max(0, config["limits"]["max_parallel_model_runs"] - busy)


def pull_once(role: str, config_path: str, invoke) -> list[str]:
    """Pull ready items into a role's columns and invoke work on them."""
    config = board_config(config_path)
    columns = [n for n, r in config["columns"].items() if r["role"] == role]
    if not columns:
        raise ValueError(f"no column for role: {role}")
    graph, labels = record_graph(), record_labels()
    cap = _global_headroom(graph, config)
    options = {"config": config, "invoke": invoke}
    claimed = []
    for column in columns:
        headroom = min(wip_headroom(column, graph, config), cap - len(claimed))
        for item in column_items(column, graph, labels, config)[:headroom]:
            if claim_and_run(item, column, role, options):
                claimed.append(item["id"])
    return claimed
