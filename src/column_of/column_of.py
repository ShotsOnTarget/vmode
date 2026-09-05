def _fits(item: dict, labels: list[str], rules: dict) -> bool:
    absent = rules.get("labels_absent", [])
    return (
        item["kind"] in rules["kinds"]
        and item["state"] in rules["states"]
        and not any(label in labels for label in absent)
    )


def column_of(item: dict, labels: list[str], config: dict) -> str | None:
    matches = [
        name for name, rules in config["columns"].items() if _fits(item, labels, rules)
    ]
    if len(matches) > 1:
        raise ValueError(f"multiple columns match: {matches}")
    if not matches and item["state"] == "in_progress":
        matches = [
            name
            for name, rules in config["columns"].items()
            if item["kind"] in rules["kinds"] and "ready" in rules["states"]
        ]
    return matches[0] if matches else None
