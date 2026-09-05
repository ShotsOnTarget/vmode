_FLAGS = {"-t", "-l", "--parent", "-a", "-d", "--description", "--type"}
_EVENT = {"--event-actor": "actor", "--event-category": "event_kind"}
_EVENT.update({"--event-target": "target", "--event-payload": "payload"})


def _flag(args: list[str], name: str, default=None):
    return args[args.index(name) + 1] if name in args else default


def _new_id(db: dict, parent: str | None) -> str:
    siblings = [i for i in db["items"].values() if i.get("parent") == parent]
    return f"{parent}.{len(siblings) + 1}" if parent else f"vm-{len(siblings) + 1:03d}"


def _title(args: list[str]) -> str:
    flags = _FLAGS | set(_EVENT)
    positional = (
        a for i, a in enumerate(args[1:], 1) if a[0] != "-" and args[i - 1] not in flags
    )
    return next(positional, "")


def fake_create(args: list[str], db: dict, now: str) -> dict:
    """`bd create` for the fake record: title, -t or --type, -l, --parent, -a,
    -d or --description, --event-*; a child id is <parent>.<n>."""
    parent = _flag(args, "--parent")
    item = {
        "id": _new_id(db, parent),
        "title": _title(args),
        "status": "open",
        "priority": 2,
    }
    item["issue_type"] = _flag(args, "--type") or _flag(args, "-t", "task")
    item.update(owner="fake", created_at=now, created_by="fake", updated_at=now)
    item["labels"] = [x for x in (_flag(args, "-l") or "").split(",") if x]
    item.update(
        assignee=_flag(args, "-a"),
        description=_flag(args, "-d", _flag(args, "--description", "")),
    )
    item.update(acceptance_criteria="", parent=parent)
    if item["issue_type"] == "event":
        item.update({field: _flag(args, flag) for flag, field in _EVENT.items()})
    db["items"][item["id"]] = item
    if parent:
        db["deps"].append(
            {"issue_id": item["id"], "depends_on_id": parent, "type": "parent-child"}
        )
    return {
        k: v for k, v in item.items() if k not in ("labels", "description", "parent")
    }
