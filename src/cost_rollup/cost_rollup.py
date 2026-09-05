from timeline.timeline import timeline


def cost_rollup(item_id: str, graph: dict) -> dict:
    result = {"item": item_id, "tokens": 0, "seconds": 0.0, "runs": 0}
    for entry in timeline(item_id, graph):
        result["tokens"] += max(entry["tokens"], 0)
        result["seconds"] += entry["seconds"]
        result["runs"] += 1
    return result
