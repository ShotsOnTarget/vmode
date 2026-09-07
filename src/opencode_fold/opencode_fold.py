import json


def opencode_fold(events: list[dict]) -> dict:
    """Fold opencode JSON events into a summary.

    Inputs: events, the JSON objects parsed one per line from the stdout of
    `opencode run --format json`, in arrival order.
    Outputs: a dict with tokens (int), turns (int or None), cost_usd (float
    or None), report (str), and error (bool).
    Side effects: none.
    """
    finishes = [e for e in events if e.get("type") == "step_finish"]

    token_totals = [
        f["part"]["tokens"]["total"]
        for f in finishes
        if isinstance(f.get("part", {}).get("tokens"), dict)
    ]
    tokens = sum(token_totals) if token_totals else -1

    turns = len(finishes) if finishes else None

    costs = [
        f["part"]["cost"]
        for f in finishes
        if isinstance(f.get("part", {}).get("cost"), (int, float))
    ]
    cost_usd = round(sum(costs), 6) if costs else None

    lines = []
    has_error = False
    for e in events:
        if e.get("type") == "text":
            lines.append(e["part"]["text"])
        elif e.get("type") == "error":
            has_error = True
            lines.append("ERROR: " + json.dumps(e.get("error"))[:500])
    report = "\n".join(lines)

    return {
        "tokens": tokens,
        "turns": turns,
        "cost_usd": cost_usd,
        "report": report,
        "error": has_error,
    }
