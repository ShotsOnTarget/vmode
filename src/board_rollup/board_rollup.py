def board_rollup(graph: dict[str, dict], care: dict[str, str]) -> list[dict]:
    """Roll up each intent with its care label, story completion counts,
    and verification completion totals and done status."""
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
        story_ids = {s["id"] for s in stories}
        stories_total = len(stories)
        stories_done = sum(1 for s in stories if s.get("state") == "done")
        verifications = [
            item
            for item in graph.values()
            if item.get("kind") == "verification" and item.get("parent") in story_ids
        ]
        verifications_total = len(verifications)
        verifications_done = sum(1 for v in verifications if v.get("state") == "done")
        verifications_complete = (
            verifications_total > 0 and verifications_done == verifications_total
        )
        rows.append(
            {
                "id": intent_id,
                "title": intent.get("title", ""),
                "state": intent.get("state", ""),
                "care": care.get(intent_id, ""),
                "stories_total": stories_total,
                "stories_done": stories_done,
                "verifications_total": verifications_total,
                "verifications_done": verifications_done,
                "verifications_complete": verifications_complete,
            }
        )

    return rows
