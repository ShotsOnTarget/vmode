from datetime import datetime


def _claude_code_names(event: dict) -> list[str]:
    content = event.get("message", {}).get("content", [])
    return [b.get("name") for b in content if b.get("type") == "tool_use"]


def _opencode_names(event: dict) -> list[str]:
    return [event.get("part", {}).get("tool")]


def _tool_names(harness: str, event: dict) -> list[str]:
    if harness == "claude_code" and event.get("type") == "assistant":
        return _claude_code_names(event)
    if harness == "opencode" and event.get("type") == "tool_use":
        return _opencode_names(event)
    return []


def run_tools(events: list[dict]) -> list[dict]:
    """Pull tool calls out of one transcript's events, as run_events returns
    them. Inputs: events, a list of dicts each with ts (an ISO 8601 string
    with a UTC offset), harness (claude_code or opencode) and event (the
    harness's own event). Outputs: one dict per tool call, in call order,
    each with name (the tool's name) and offset (seconds from the first
    line's ts to that line's ts, a float rounded to three decimals). A
    Claude Code assistant event with several tool_use blocks in its
    message.content gives one entry per block, all sharing that line's
    offset; an opencode event whose own type is tool_use gives one entry
    from its part.tool. Any other harness or event shape contributes
    nothing. An empty events list gives an empty list. Side effects: none.
    """
    if not events:
        return []
    start = datetime.fromisoformat(events[0]["ts"])
    calls = []
    for line in events:
        names = _tool_names(line.get("harness"), line.get("event", {}))
        if not names:
            continue
        offset = round((datetime.fromisoformat(line["ts"]) - start).total_seconds(), 3)
        calls.extend({"name": name, "offset": offset} for name in names)
    return calls
