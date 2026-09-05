from wiki_read.wiki_read import wiki_read
from wiki_write.wiki_write import wiki_write


def wiki_touch(root: str, page_id: str, now: str) -> dict:
    """Record a use of a wiki page by bumping its usage stats."""
    page = wiki_read(root, page_id)
    page["last_used"] = now
    page["times_used"] = page["times_used"] + 1
    wiki_write(root, page)
    return page
