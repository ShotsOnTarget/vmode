from record_run.record_run import record_run

_RIGHT_SIDE_KINDS = ("test", "verification", "validation")
_KINDS = ("intent", "story", "code", "proposal", "note") + _RIGHT_SIDE_KINDS


def _validate(kind: str, owner: str, parent: str | None) -> None:
    if kind not in _KINDS:
        raise ValueError(f"kind must be one of {_KINDS}, got {kind!r}")
    if not owner:
        raise ValueError("owner must not be empty")
    if parent is None and kind != "intent":
        raise ValueError("parent is required unless kind is intent")


def _build_args(kind: str, title: str, owner: str, parent: str | None) -> list[str]:
    args = [
        "create",
        title,
        "-t",
        "epic" if kind == "intent" else "task",
        "-l",
        f"kind:{kind},state:waiting,owner:{owner}",
        "--no-inherit-labels",
    ]
    if parent and kind not in _RIGHT_SIDE_KINDS:
        args += ["--parent", parent]
    return args


def record_create_item(
    kind: str, title: str, owner: str, parent: str | None = None
) -> dict:
    _validate(kind, owner, parent)

    args = _build_args(kind, title, owner, parent)
    result = record_run(args)
    new_id = result["id"]

    if kind in _RIGHT_SIDE_KINDS:
        record_run(["dep", "add", new_id, parent, "-t", "validates"])

    return dict(
        id=new_id, kind=kind, title=title, owner=owner, parent=parent, state="waiting"
    )
