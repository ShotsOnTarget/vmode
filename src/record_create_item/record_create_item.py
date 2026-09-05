from record_run.record_run import record_run

_RIGHT_SIDE_KINDS = ("test", "verification", "validation")
_KINDS = ("intent", "story", "code", "proposal", "note", "pattern") + _RIGHT_SIDE_KINDS


def _validate(kind: str, owner: str, parent: str | None) -> None:
    if kind not in _KINDS:
        raise ValueError(f"kind must be one of {_KINDS}, got {kind!r}")
    if not owner:
        raise ValueError("owner must not be empty")
    if parent is None and kind != "intent":
        raise ValueError("parent is required unless kind is intent")


def _tree_parent(kind: str, parent: str | None) -> str | None:
    """Where the item hangs: a test hangs beside the code it checks."""
    if kind == "test":
        return record_run(["show", parent])[0].get("parent")
    return None if kind in _RIGHT_SIDE_KINDS else parent


def record_create_item(
    kind: str, title: str, owner: str, parent: str | None = None
) -> dict:
    """Create one work item. For test, verification and validation, parent
    is the item it checks (a validates link); a test also hangs under that
    code job's Story as its sibling. Other kinds hang under parent."""
    _validate(kind, owner, parent)
    args = ["create", title, "-t", "epic" if kind == "intent" else "task"]
    args += ["-l", f"kind:{kind},state:waiting,owner:{owner}", "--no-inherit-labels"]
    tree_parent = _tree_parent(kind, parent)
    if tree_parent:
        args += ["--parent", tree_parent]
    new_id = record_run(args)["id"]
    if kind in _RIGHT_SIDE_KINDS:
        record_run(["dep", "add", new_id, parent, "-t", "validates"])
    return dict(
        id=new_id, kind=kind, title=title, owner=owner, parent=parent, state="waiting"
    )
