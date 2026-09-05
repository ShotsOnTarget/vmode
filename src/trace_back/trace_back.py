def trace_back(item_id: str, graph: dict[str, dict]) -> list[dict]:
    """Walk the parent chain of an item to its root, returning the path."""
    if item_id not in graph:
        raise ValueError(item_id)

    result = []
    visited = set()
    current_id = item_id

    while True:
        if current_id in visited:
            raise ValueError("cycle")
        visited.add(current_id)

        item = graph[current_id]
        result.append(
            {
                "id": current_id,
                "kind": item.get("kind"),
                "title": item.get("title"),
            }
        )

        parent_id = item.get("parent")
        if not parent_id:
            break
        current_id = parent_id

    return result
