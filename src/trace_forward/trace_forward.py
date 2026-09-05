def trace_forward(item_id: str, graph: dict[str, dict]) -> dict:
    """Build the forward-trace tree of items descending from a given item id."""
    if item_id not in graph:
        raise ValueError(f"item_id not in graph: {item_id}")
    return _build(item_id, graph, set())


def _build(item_id: str, graph: dict[str, dict], visited: set) -> dict:
    visited = visited | {item_id}
    node = graph[item_id]
    child_ids = set()
    for other_id, other in graph.items():
        if other.get("parent") == item_id:
            child_ids.add(other_id)
        if item_id in (other.get("checks") or []):
            child_ids.add(other_id)
    children = [
        _build(child_id, graph, visited)
        for child_id in sorted(child_ids)
        if child_id not in visited
    ]
    return {
        "id": item_id,
        "kind": node.get("kind"),
        "title": node.get("title"),
        "children": children,
    }
