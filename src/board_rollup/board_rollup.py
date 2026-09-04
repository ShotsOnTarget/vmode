def board_rollup(graph: dict[str, dict], care: dict[str, str]) -> list[dict]:
    intents = [item for item in graph.values() if item.get("kind") == "intent"]
    intents.sort(key=lambda item: item["id"])

    rows = []
    for intent in intents:
        intent_id = intent["id"]
        stories = [
            item
            for item in graph.values()
            if item.get("kind") == "story" and item.get("parent") == intent_id
        ]
        stories_total = len(stories)
        stories_done = sum(1 for s in stories if s.get("state") == "done")
        rows.append(
            {
                "id": intent_id,
                "title": intent.get("title", ""),
                "state": intent.get("state", ""),
                "care": care.get(intent_id, ""),
                "stories_total": stories_total,
                "stories_done": stories_done,
            }
        )

    return rows
