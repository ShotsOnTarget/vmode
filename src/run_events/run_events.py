import json


def run_events(path: str) -> list[dict]:
    """Read one transcript file left by transcript_write. Inputs: path, the
    file's path, UTF-8 text with one JSON object per line carrying the keys
    ts, item, harness, model, effort, role and event. Outputs: the parsed
    line objects as a list of dicts, in file order; a blank line, a
    whitespace-only line, a line that is not valid JSON, and a line whose
    JSON is not an object are all skipped. An empty file gives an empty
    list. Side effects: none; a missing path lets FileNotFoundError reach
    the caller.
    """
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                events.append(parsed)
    return events
