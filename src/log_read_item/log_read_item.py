import json
import os


def log_read_item(path: str, item_id: str) -> list[dict]:
    if not os.path.isfile(path):
        return []
    results = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                raise ValueError(f"invalid JSON line in {path}: {line}")
            if entry.get("item") == item_id:
                results.append(entry)
    return results
