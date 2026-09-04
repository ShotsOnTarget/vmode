import json
import os

from board_config.board_config import board_config
from claim_item.claim_item import claim_item
from column_items.column_items import column_items
from record_add_note.record_add_note import record_add_note
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_set_state.record_set_state import record_set_state
from wip_headroom.wip_headroom import wip_headroom


def _global_headroom(graph: dict, config: dict) -> int:
    tiers = {k: r["tier"] for r in config["columns"].values() for k in r["kinds"]}
    busy = sum(
        item["state"] == "in_progress"
        and tiers.get(item["kind"], "") not in ("none", "human")
        for item in graph.values()
    )
    return max(0, config["limits"]["max_parallel_model_runs"] - busy)


def _claim_and_invoke(item: dict, column: str, role: str, invoke) -> str:
    claim_item(item["id"], role + "-" + str(os.getpid()))
    try:
        usage = invoke(item, column)
        record_add_note(item["id"], "usage: " + json.dumps(usage))
        record_set_state(item["id"], "checking")
    except Exception as exc:
        record_set_state(item["id"], "ready")
        record_add_note(item["id"], "release: " + str(exc)[:200])
    return item["id"]


def pull_once(role: str, config_path: str, invoke) -> list[str]:
    config = board_config(config_path)
    columns = [n for n, r in config["columns"].items() if r["role"] == role]
    if not columns:
        raise ValueError(f"no column for role: {role}")
    graph = record_graph()
    labels = record_labels()
    remaining = _global_headroom(graph, config)
    claimed = []
    for column in columns:
        headroom = min(wip_headroom(column, graph, config), remaining)
        for item in column_items(column, graph, labels, config)[:headroom]:
            claimed.append(_claim_and_invoke(item, column, role, invoke))
            remaining -= 1
    return claimed
