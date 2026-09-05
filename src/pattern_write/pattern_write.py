import os
import tempfile

from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run

_KEYS = ("title", "pattern", "fix", "cited")


def pattern_write(parent_id: str, page: dict) -> str:
    """Create a pattern item: what keeps happening, its fix, and its evidence.

    page: title, pattern (one paragraph), fix (one paragraph naming the file
    or item to change), cited (two or more item ids the pattern was learned
    from), optional cost (tokens). The item hangs under parent_id (the Story
    or Intent it was learned from), links relates-to each cited id, carries
    labels used:0 and last_used:<date>, and returns the new id.
    """
    missing = [k for k in _KEYS if not page.get(k)]
    if missing or len(page["cited"]) < 2:
        raise ValueError(f"pattern needs {', '.join(_KEYS)} and two cited items")
    item = record_create_item("pattern", page["title"], "analyst", parent_id)
    body = f"## Pattern\n\n{page['pattern']}\n\n## Fix\n\n{page['fix']}\n"
    body += f"\ncost: {int(page.get('cost', 0))}\n"
    fd, path = tempfile.mkstemp(suffix=".md", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(body)
    try:
        record_run(["update", item["id"], "--body-file", path])
    finally:
        os.remove(path)
    for cited in page["cited"]:
        record_run(["dep", "add", item["id"], cited, "-t", "relates-to"])
    record_run(["label", "add", item["id"], "used:0"])
    record_run(
        ["label", "add", item["id"], f"last_used:{page.get('created', '')[:10]}"]
    )
    return item["id"]
