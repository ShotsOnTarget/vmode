import os
from datetime import datetime, timedelta

from wiki_read.wiki_read import wiki_read


def wiki_stale(root: str, days: int, now: str) -> list[str]:
    if not root or not os.path.isdir(root):
        return []

    now_dt = datetime.fromisoformat(now)
    cutoff = now_dt - timedelta(days=days)

    stale = []
    for name in os.listdir(root):
        if not name.endswith(".md") or name == "README.md":
            continue
        page_id = name[: -len(".md")]
        page = wiki_read(root, page_id)
        last_used = datetime.fromisoformat(page["last_used"])
        if last_used < cutoff:
            stale.append(page_id)

    return sorted(stale)
