from timeline.timeline import timeline


def _nearest_story(item_id, graph):
    visited = set()
    current = item_id
    while current is not None and current not in visited:
        visited.add(current)
        node = graph.get(current)
        if node is None:
            return None
        if node.get("kind") == "story":
            return current
        current = node.get("parent")
    return None


def _group_ready(events, graph):
    ready_by_story: dict[str, list[dict]] = {}
    for event in events:
        target = event.get("item")
        is_ready = event.get("gate") == "ready"
        if is_ready and graph.get(target, {}).get("kind") == "story":
            ready_by_story.setdefault(target, []).append(event)
    return ready_by_story


def _count_by_story(graph, stories, item_ids):
    counts = {story: 0 for story in stories}
    for item_id in item_ids:
        story = _nearest_story(item_id, graph)
        if story in counts:
            counts[story] += 1
    return counts


def _row(story, readies, bounces, blocked):
    inputs = readies[-1].get("inputs") or {}
    setting = "/".join(
        inputs.get(key) or "none" for key in ("harness", "model", "effort")
    )
    return {
        "story": story,
        "setting": setting,
        "pairs": int(inputs.get("pairs") or 0),
        "tokens": sum(max(event.get("tokens", 0), 0) for event in readies),
        "usd": float(sum((event.get("usd") or 0.0) for event in readies)),
        "bounces": bounces[story],
        "blocked": blocked[story],
    }


def cutter_gather(item_id: str, graph: dict) -> list[dict]:
    """Measure every Story at or under item_id from its logged events.

    item_id: any id in graph. graph: the dict record_graph() returns.
    Returns one dict per Story with a ready event on itself, sorted by
    story id, with keys story, setting, pairs, tokens, usd, bounces and
    blocked. Reads the log through one call to timeline(item_id, graph).
    Raises ValueError when item_id is not a key of graph.
    """
    events = timeline(item_id, graph)
    ready_by_story = _group_ready(events, graph)
    bounce_ids = (
        e.get("item")
        for e in events
        if e.get("gate") == "built"
        and (e.get("inputs") or {}).get("action") in ("bounce", "escalate")
    )
    note_ids = (
        n_id
        for n_id, n in graph.items()
        if n.get("kind") == "note" and n.get("owner") == "supervisor"
    )
    bounces = _count_by_story(graph, ready_by_story, bounce_ids)
    blocked = _count_by_story(graph, ready_by_story, note_ids)
    return [
        _row(story, ready_by_story[story], bounces, blocked)
        for story in sorted(ready_by_story)
    ]
