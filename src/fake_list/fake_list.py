def _flag(args: list[str], name: str):
    return args[args.index(name) + 1] if name in args else None


def _keep(item: dict, args: list[str]) -> bool:
    if "--all" not in args and item["status"] == "closed":
        return False
    kind, exclude, label = (
        _flag(args, "--type"),
        _flag(args, "--exclude-type"),
        _flag(args, "-l"),
    )
    wanted = kind is None or item["issue_type"] == kind
    return (
        wanted
        and item["issue_type"] != exclude
        and (label is None or label in item["labels"])
    )


def fake_list(args: list[str], db: dict) -> list[dict]:
    """`bd list` for the fake record: open items unless --all; --type and
    --exclude-type by issue_type; -l by label; each row carries its
    dependencies as {issue_id, depends_on_id, type} and a comment_count."""
    out = []
    for item in db["items"].values():
        if _keep(item, args):
            deps = [d for d in db["deps"] if d["issue_id"] == item["id"]]
            count = len(db["comments"].get(item["id"], []))
            out.append({**item, "dependencies": deps, "comment_count": count})
    return out
