def claude_fold(result: dict) -> dict:
    """Fold a Claude Code result event into a summary.

    Inputs: result, the parsed `result` event of one Claude Code run (the
    last line of `claude -p --output-format stream-json --verbose`, the same
    object `claude -p --output-format json` prints).
    Outputs: a dict with tokens (int), turns (int or None), cost_usd (float
    or None), report (str), and error (bool).
    Side effects: none.
    """
    usage = result.get("usage")
    if isinstance(usage, dict) and usage:
        tokens = (
            usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
            + usage.get("output_tokens", 0)
        )
    else:
        tokens = -1

    turns = result.get("num_turns")
    cost_usd = result.get("total_cost_usd")
    report = result.get("result") or ""

    if "is_error" in result:
        error = bool(result["is_error"])
    else:
        error = result.get("subtype") != "success"

    return {
        "tokens": tokens,
        "turns": turns,
        "cost_usd": cost_usd,
        "report": report,
        "error": error,
    }
