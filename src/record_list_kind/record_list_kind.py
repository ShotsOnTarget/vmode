from record_run.record_run import record_run, RecordError

VALID_KINDS = {
    "intent",
    "story",
    "validation",
    "verification",
    "code",
    "test",
}


def _state_from_labels(labels: list) -> str | None:
    for label in labels or []:
        if isinstance(label, str) and label.startswith("state:"):
            return label.split(":", 1)[1]
    return None


def record_list_kind(kind: str) -> list[dict]:
    if kind not in VALID_KINDS:
        raise ValueError(f"invalid kind: {kind}")

    items = record_run(["list", "--all", "-l", f"kind:{kind}"])

    result = []
    for item in items:
        result.append(
            {
                "id": item.get("id"),
                "kind": kind,
                "title": item.get("title"),
                "owner": item.get("assignee"),
                "state": _state_from_labels(item.get("labels")),
            }
        )
    return result
