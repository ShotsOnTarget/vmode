def _owner_allowed(item: dict, rules: dict) -> bool:
    owners = rules.get("owners")
    return owners is None or item["owner"] in owners


def _fits(item: dict, labels: list[str], rules: dict) -> bool:
    absent = rules.get("labels_absent", [])
    return (
        item["kind"] in rules["kinds"]
        and item["state"] in rules["states"]
        and _owner_allowed(item, rules)
        and not any(label in labels for label in absent)
    )


def column_of(item: dict, labels: list[str], config: dict) -> str | None:
    """Determine which board column a graph item belongs in."""
    matches = [
        name for name, rules in config["columns"].items() if _fits(item, labels, rules)
    ]
    if len(matches) > 1:
        raise ValueError(f"multiple columns match: {matches}")
    if not matches and item["state"] == "in_progress":
        matches = [
            name
            for name, rules in config["columns"].items()
            if item["kind"] in rules["kinds"]
            and "ready" in rules["states"]
            and _owner_allowed(item, rules)
        ]
    return matches[0] if matches else None
