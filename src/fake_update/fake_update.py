def _flag(args: list[str], name: str):
    return args[args.index(name) + 1] if name in args else None


def _claim(item: dict, actor: str) -> None:
    if item.get("assignee") and item["assignee"] != actor:
        raise ValueError("issue already claimed by another actor")
    item.update(assignee=actor, status="in_progress")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


_SETTERS = {
    "-a": lambda item, v: item.update(assignee=v or None),
    "-s": lambda item, v: item.update(status=v),
    "--body-file": lambda item, v: item.update(description=_read(v)),
    "--acceptance": lambda item, v: item.update(acceptance_criteria=v),
    "--add-label": lambda item, v: item["labels"].append(v),
    "--parent": lambda item, v: item.update(parent=v),
}


def fake_update(args: list[str], db: dict, now: str) -> list[dict]:
    """`bd update <id>` for the fake record: --claim --actor, -a, -s,
    --body-file, --acceptance, --add-label, --parent. Returns [item]."""
    item = db["items"][args[1]]
    if "--claim" in args:
        _claim(item, _flag(args, "--actor"))
    for flag, setter in _SETTERS.items():
        if flag in args:
            setter(item, _flag(args, flag))
    item["updated_at"] = now
    return [dict(item)]
