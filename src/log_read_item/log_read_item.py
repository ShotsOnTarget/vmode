import json
import os


def _parse_line(path: str, line: str) -> dict:
    try:
        return json.loads(line)
    except json.JSONDecodeError as err:
        raise ValueError(f"invalid JSON line in {path}: {line}") from err


def log_read_item(path: str, item_id: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    results = []
    with open(path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            entry = _parse_line(path, line)
            if entry.get("item") == item_id:
                results.append(entry)
    return results
