from timeline.timeline import timeline


def cost_rollup(item_id: str, graph: dict) -> dict:
    """Cost of an item and everything under it, one Built or Ready event per run.

    Sums tokens, seconds, usd (the harness cost, when recorded) and turns
    over the Built or Ready events in the timeline; a test job's Proven event repeats
    its Built figures and is not counted again. runs is the Built or Ready count.
    Returns {'item', 'tokens', 'seconds', 'usd', 'turns', 'runs'}.
    """
    result = {"item": item_id, "tokens": 0, "seconds": 0.0, "usd": 0.0, "turns": 0}
    result["runs"] = 0
    for entry in timeline(item_id, graph):
        if entry.get("gate") not in ("built", "ready"):
            continue
        result["tokens"] += max(entry.get("tokens", 0), 0)
        result["seconds"] += entry.get("seconds", 0.0)
        result["usd"] += entry.get("usd") or 0.0
        result["turns"] += entry.get("turns") or 0
        result["runs"] += 1
    return result
