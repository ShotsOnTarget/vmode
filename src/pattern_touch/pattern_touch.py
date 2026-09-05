from record_run.record_run import record_run


def pattern_touch(pattern_id: str, today: str) -> dict:
    """Mark a pattern as used today: used:<n> becomes used:<n+1> and
    last_used:<date> becomes today. Returns {'id', 'used', 'last_used'}."""
    labels = record_run(["label", "list", pattern_id])
    labels = [x if isinstance(x, str) else x.get("name", "") for x in labels]
    if "kind:pattern" not in labels:
        raise ValueError(f"not a pattern: {pattern_id}")
    used = 0
    for name in labels:
        if name.startswith("used:") or name.startswith("last_used:"):
            used = int(name[5:]) if name.startswith("used:") else used
            record_run(["label", "remove", pattern_id, name])
    record_run(["label", "add", pattern_id, f"used:{used + 1}"])
    record_run(["label", "add", pattern_id, f"last_used:{today}"])
    return {"id": pattern_id, "used": used + 1, "last_used": today}
