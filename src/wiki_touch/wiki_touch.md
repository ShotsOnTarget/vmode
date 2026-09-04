purpose: record a use of a wiki page by bumping its usage stats
signature: wiki_touch(root: str, page_id: str, now: str) -> dict
inputs: root (wiki directory), page_id (page identifier), now (ISO-8601 timestamp string)
outputs: the updated page dict, with last_used == now and times_used incremented by one
side effects: rewrites the page file on disk via wiki_write
work item id: 0002-2-wiki_touch-code
