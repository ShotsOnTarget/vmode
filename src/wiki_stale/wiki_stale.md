purpose: find wiki page ids whose last_used is older than a day threshold
signature: wiki_stale(root: str, days: int, now: str) -> list[str]
inputs: root: wiki directory. days: staleness threshold in days. now: ISO-8601 string supplied by the caller.
outputs: sorted list of page ids whose last_used is more than `days` days before now; empty list if root is empty or missing
side effects: none
work item id: 0002-2-wiki_stale-code
