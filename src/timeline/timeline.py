from log_read_item.log_read_item import log_read_item
from trace_forward.trace_forward import trace_forward


def _flatten(node: dict) -> list[str]:
    ids = [node["id"]]
    for child in node["children"]:
        ids.extend(_flatten(child))
    return ids


def timeline(item_id: str, graph: dict) -> list[dict]:
    """Return the log events for an item and everything under it, in time order.

    item_id is any work item id; graph is the dict record_graph() returns.
    Returns each log entry from log_read_item once, even when the item it
    belongs to is reachable by more than one path through the graph, sorted
    oldest first by ts. Has no side effects.
    """
    ids = _flatten(trace_forward(item_id, graph))
    seen = set()
    events = []
    for id_ in ids:
        for entry in log_read_item(id_):
            if entry["id"] not in seen:
                seen.add(entry["id"])
                events.append(entry)
    return sorted(events, key=lambda entry: entry["ts"])
