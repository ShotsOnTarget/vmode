def _last_result(events: list[dict]) -> dict:
    result = None
    for event in events:
        if event.get("type") == "result":
            result = event
    if result is None:
        raise ValueError("no result event in stream")
    return result


def _tokens(result: dict) -> int:
    usage = result.get("usage")
    if not isinstance(usage, dict) or not usage:
        return -1
    return (
        usage.get("input_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0)
        + usage.get("output_tokens", 0)
    )


def claude_fold(events: list[dict]) -> dict:
    """Fold a Claude Code event stream into a summary.

    Inputs: events, the JSON objects parsed one per line from the stdout of
    `claude -p --output-format stream-json --verbose`, in arrival order.
    Outputs: a dict with tokens (int), turns (int or None), cost_usd (float
    or None), report (str), and error (bool), taken from the last event
    whose `type` is `result`.
    Side effects: none.
    """
    result = _last_result(events)

    if "is_error" in result:
        error = bool(result["is_error"])
    else:
        error = result.get("subtype") != "success"

    return {
        "tokens": _tokens(result),
        "turns": result.get("num_turns"),
        "cost_usd": result.get("total_cost_usd"),
        "report": result.get("result") or "",
        "error": error,
    }
