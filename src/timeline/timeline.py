from log_read_item.log_read_item import log_read_item
from trace_forward.trace_forward import trace_forward

_LOG_PATH = "work/supervisor-log.jsonl"


def _flatten(node: dict) -> list[str]:
    ids = [node["id"]]
    for child in node["children"]:
        ids.extend(_flatten(child))
    return ids


def timeline(item_id: str, graph: dict) -> list[dict]:
    ids = _flatten(trace_forward(item_id, graph))
    events = []
    for id_ in ids:
        events.extend(log_read_item(_LOG_PATH, id_))
    return sorted(events, key=lambda entry: entry["ts"])
