from datetime import date


def _last_used(labels: list[str]) -> date | None:
    for name in labels:
        if name.startswith("last_used:") and len(name) >= 20:
            return date.fromisoformat(name[10:20])
    return None


def pattern_stale(
    labels: dict[str, list[str]], today: str, days: int = 90
) -> list[str]:
    """Ids of patterns not used for `days` days by `today` (YYYY-MM-DD).

    labels is record_labels(): id -> label list. A pattern is one with
    kind:pattern; its last use is the last_used:<date> label; a pattern with
    no readable date counts as stale. Sorted by id.
    """
    limit = date.fromisoformat(today)
    stale = []
    for item_id, names in labels.items():
        if "kind:pattern" not in names:
            continue
        last = _last_used(names)
        if last is None or (limit - last).days >= days:
            stale.append(item_id)
    return sorted(stale)
