import re

from record_run.record_run import record_run


def _label(labels: list[str], prefix: str, default: str) -> str:
    return next((x[len(prefix) :] for x in labels if x.startswith(prefix)), default)


def pattern_read(pattern_id: str) -> dict:
    """One pattern item as a dict: id, title, pattern, fix, cost, cited,
    used, last_used. cited are the ids it relates to; used and last_used
    come from its labels. Raises ValueError when the item is not a pattern."""
    row = record_run(["show", pattern_id])[0]
    labels = row.get("labels", [])
    if "kind:pattern" not in labels:
        raise ValueError(f"not a pattern: {pattern_id}")
    text = row.get("description") or ""
    pattern = re.search(r"## Pattern\s+(.*?)\s+## Fix", text, re.S)
    fix = re.search(r"## Fix\s+(.*?)(?:\s+cost:|\Z)", text, re.S)
    cost = re.search(r"cost:\s*(\d+)", text)
    cited = [
        d["id"]
        for d in row.get("dependencies", [])
        if d.get("dependency_type") == "relates-to"
    ]
    return {
        "id": pattern_id,
        "title": row.get("title", ""),
        "pattern": pattern.group(1).strip() if pattern else "",
        "fix": fix.group(1).strip() if fix else "",
        "cost": int(cost.group(1)) if cost else 0,
        "cited": cited,
        "used": int(_label(labels, "used:", "0")),
        "last_used": _label(labels, "last_used:", ""),
    }
