import pathlib

from board_columns.board_columns import board_columns
from board_config.board_config import board_config
from board_decide.board_decide import board_decide
from board_rollup.board_rollup import board_rollup
from board_tree.board_tree import board_tree
from columns_rows.columns_rows import columns_rows
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_set_state.record_set_state import record_set_state
from record_show_item.record_show_item import record_show_item
from story_status.story_status import story_status
from timeline.timeline import timeline

CONFIG = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _care(labels: dict) -> dict:
    care = {}
    for item_id, item_labels in labels.items():
        for label in item_labels:
            if label.startswith("care:"):
                care[item_id] = label[len("care:") :]
    return care


def board_api(name: str, query: dict, body: dict) -> object:
    """Dispatch one board API call by name to its handler."""
    handlers = {
        "intents": lambda: board_rollup(record_graph(), _care(record_labels())),
        "tree": lambda: board_tree(query["id"], record_graph()),
        "item": lambda: record_show_item(query["id"]),
        "timeline": lambda: timeline(query["id"], record_graph()),
        "columns": lambda: _columns(board_config(CONFIG)),
        "decide": lambda: board_decide(
            body.get("intent", ""), body.get("decision", ""), body.get("reason", "")
        ),
        "release": lambda: _release(body["id"]),
        "status": lambda: story_status(query["id"], record_graph(), record_labels()),
    }
    return handlers[name]()


def _release(item_id: str) -> dict:
    item = record_show_item(item_id)
    if item["kind"] != "intent" or item["state"] != "waiting":
        raise ValueError(f"not a waiting intent: {item_id}")
    return record_set_state(item_id, "ready")


def _columns(config: dict) -> list[dict]:
    rows = columns_rows(config)
    labels = {row["id"]: row.get("labels", []) for row in rows}
    return board_columns(record_graph(rows), labels, config)
