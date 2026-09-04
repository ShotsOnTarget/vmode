from record_run.record_run import record_run, RecordError

_KINDS = ("intent", "story", "code", "test", "verification", "validation")


def record_create_item(
    kind: str, title: str, owner: str, parent: str | None = None
) -> dict:
    if kind not in _KINDS:
        raise ValueError(f"kind must be one of {_KINDS}, got {kind!r}")
    if not owner:
        raise ValueError("owner must not be empty")
    if parent is None and kind != "intent":
        raise ValueError("parent is required unless kind is intent")

    args = [
        "create",
        title,
        "-t",
        "epic" if kind == "intent" else "task",
        "-l",
        f"kind:{kind},state:waiting",
        "-a",
        owner,
        "--no-inherit-labels",
    ]
    if parent:
        args += ["--parent", parent]

    result = record_run(args)

    return {
        "id": result["id"],
        "kind": kind,
        "title": title,
        "owner": owner,
        "parent": parent,
        "state": "waiting",
    }
