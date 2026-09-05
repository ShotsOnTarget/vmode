from log_read_item.log_read_item import log_read_item
from trace_forward.trace_forward import trace_forward


def _flatten(node: dict) -> list[str]:
    ids = [node["id"]]
    for child in node["children"]:
        ids.extend(_flatten(child))
    return ids


def timeline(item_id: str, graph: dict) -> list[dict]:
    """Return the log events for an item and everything under it, in time order."""
    ids = _flatten(trace_forward(item_id, graph))
    events = []
    for id_ in ids:
        events.extend(log_read_item(id_))
    return sorted(events, key=lambda entry: entry["ts"])
