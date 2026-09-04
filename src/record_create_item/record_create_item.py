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

    right_side = kind in ("test", "verification", "validation")

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
    if parent and not right_side:
        args += ["--parent", parent]

    result = record_run(args)
    new_id = result["id"]

    if right_side:
        record_run(["dep", "add", new_id, parent, "-t", "validates"])

    return {
        "id": new_id,
        "kind": kind,
        "title": title,
        "owner": owner,
        "parent": parent,
        "state": "waiting",
    }
