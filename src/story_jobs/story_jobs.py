def story_jobs(story_id: str, graph: dict) -> dict:
    if story_id not in graph:
        raise ValueError(story_id)

    has_intent = False
    visited = set()
    current = graph[story_id].get("parent")
    while current is not None and current not in visited and current in graph:
        visited.add(current)
        item = graph[current]
        has_intent = item.get("kind") == "intent"
        if has_intent:
            break
        current = item.get("parent")

    code = sorted(
        item_id
        for item_id, item in graph.items()
        if item.get("kind") == "code" and item.get("parent") == story_id
    )

    tests = {}
    for code_id in code:
        tests[code_id] = sorted(
            item_id
            for item_id, item in graph.items()
            if item.get("kind") == "test" and code_id in item.get("checks", [])
        )

    return {"has_intent": has_intent, "code": code, "tests": tests}
