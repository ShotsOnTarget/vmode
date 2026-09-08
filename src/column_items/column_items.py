from column_of.column_of import column_of

# Story states whose jobs the Ready gate has released: the set prove_once uses.
_RELEASED = ("ready", "checking", "done")


def _needs_unmet(item: dict, graph: dict) -> bool:
    needs = item.get("needs", [])
    return any(graph.get(need, {}).get("state") != "done" for need in needs)


def _story_unreleased(item: dict, graph: dict) -> bool:
    """A job whose Story, when it is in graph, the gate has not released."""
    if item["kind"] not in ("code", "test"):
        return False
    story = graph.get(item.get("parent") or "", {})
    return story.get("kind") == "story" and story["state"] not in _RELEASED


def _held(item: dict, graph: dict) -> bool:
    return (
        item["state"] == "in_progress"
        or _needs_unmet(item, graph)
        or _story_unreleased(item, graph)
    )


def column_items(
    name: str, graph: dict, labels: dict[str, list[str]], config: dict
) -> list[dict]:
    """Items a puller may take from one column, sorted by id.

    An item is listed when column_of places it in the column and, for a
    pulling column (tier not 'none'), every item it needs is done and, for
    a code or test job, its Story is one the Ready gate has released
    (ready, checking or done) whenever that Story is in graph. A job's own
    ready state is only a copy of its Story's, kept by the Supervisor's
    pass, so a Story blocked or refused a moment ago can still have ready
    jobs under it; reading the Story here closes that window. Gating
    columns list everything in their states: needs gate pulling, never
    gating. A claimed (in_progress) item is never offered to a puller.
    """
    if name not in config["columns"]:
        raise ValueError(f"not a column: {name}")
    filtered = config["columns"][name]["tier"] != "none"
    items = [
        item
        for item_id, item in graph.items()
        if column_of(item, labels.get(item_id, []), config) == name
        and not (filtered and _held(item, graph))
    ]
    return sorted(items, key=lambda i: i["id"])
