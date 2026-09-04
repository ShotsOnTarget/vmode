import json
import os


def _matches_item(line_item, item_id: str, prefix: str) -> bool:
    return line_item == item_id or (
        isinstance(line_item, str) and line_item.startswith(prefix)
    )


def _parse_record(line: str) -> dict:
    try:
        return json.loads(line)
    except ValueError as err:
        raise ValueError("invalid JSON line: " + line) from err


def _numeric(value, default):
    return value if isinstance(value, (int, float)) else default


def _apply_record(result: dict, record: dict) -> None:
    result["tokens"] += max(_numeric(record.get("tokens", 0), 0), 0)
    result["seconds"] += _numeric(record.get("seconds", 0.0), 0.0)
    result["runs"] += 1


def cost_rollup(path: str, item_id: str) -> dict:
    result = {"item": item_id, "tokens": 0, "seconds": 0.0, "runs": 0}
    if not os.path.exists(path):
        return result
    prefix = item_id + "-"
    with open(path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            record = _parse_record(line)
            if _matches_item(record.get("item"), item_id, prefix):
                _apply_record(result, record)
    return result
