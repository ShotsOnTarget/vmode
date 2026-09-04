def wip_headroom(name: str, graph: dict, config: dict) -> int:
    if name not in config["columns"]:
        raise ValueError(f"not a column: {name}")
    kinds = config["columns"][name]["kinds"]
    in_progress = sum(
        1
        for item in graph.values()
        if item["kind"] in kinds and item["state"] == "in_progress"
    )
    return max(0, config["columns"][name]["wip"] - in_progress)
