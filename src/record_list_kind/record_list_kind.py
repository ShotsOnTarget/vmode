from record_run.record_run import record_run

VALID_KINDS = {
    "intent",
    "story",
    "validation",
    "verification",
    "code",
    "test",
}


def _label_value(labels: list, prefix: str) -> str | None:
    for label in labels or []:
        if isinstance(label, str) and label.startswith(prefix):
            return label.split(":", 1)[1]
    return None


def record_list_kind(kind: str) -> list[dict]:
    """List every record item of a given kind, including closed ones."""
    if kind not in VALID_KINDS:
        raise ValueError(f"invalid kind: {kind}")

    items = record_run(["list", "--all", "-l", f"kind:{kind}"])

    result = []
    for item in items:
        labels = item.get("labels")
        result.append(
            {
                "id": item.get("id"),
                "kind": kind,
                "title": item.get("title"),
                "owner": _label_value(labels, "owner:"),
                "state": _label_value(labels, "state:"),
            }
        )
    return result
