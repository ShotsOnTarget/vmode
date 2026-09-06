"""Split a Story checklist into its items."""


def checklist_items(text: str) -> list[str]:
    """Split checklist text into ordered items without numbers.

    Args:
        text: A Story checklist numbered ``1. ``, ``2. ``, ... .

    Returns:
        The items in order, each stripped of whitespace.

    Side effects:
        None. Pure.
    """
    if text.strip() == "":
        return []
    lead = text.lstrip()
    if not lead.startswith("1. "):
        return [text.strip()]
    current = lead[len("1. ") :]
    items = []
    n = 2
    while True:
        marker = f"{n}. "
        idx = current.find(marker)
        if idx == -1:
            items.append(current.strip())
            return items
        items.append(current[:idx].strip())
        current = current[idx + len(marker) :]
        n += 1
