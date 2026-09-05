def _label(args: list[str], db: dict) -> list:
    item, name = db["items"][args[2]], args[3] if len(args) > 3 else ""
    if args[1] == "list":
        return list(item["labels"])
    if args[1] == "add" and name not in item["labels"]:
        item["labels"].append(name)
    if args[1] == "remove" and name in item["labels"]:
        item["labels"].remove(name)
    return [{"issue_id": args[2], "label": name, "status": "added"}]


def _dep(args: list[str], db: dict) -> dict | list:
    if args[1] == "list":
        rows = (d for d in db["deps"] if d["issue_id"] == args[2])
        return [
            {**db["items"][d["depends_on_id"]], "dependency_type": d["type"]}
            for d in rows
        ]
    src, blocked = args[2], "--blocked-by" in args
    dst = args[args.index("--blocked-by") + 1] if blocked else args[3]
    kind = "blocks" if blocked else args[args.index("-t") + 1]
    if db["items"][src].get("parent") == dst and kind != "parent-child":
        raise ValueError("cannot add a dependency from a child to its parent")
    db["deps"].append({"issue_id": src, "depends_on_id": dst, "type": kind})
    return {"depends_on_id": dst, "issue_id": src, "status": "added", "type": kind}


def _comment(args: list[str], db: dict, now: str) -> dict:
    rows = db["comments"].setdefault(args[1], [])
    row = {"id": f"c{len(rows) + 1}-{args[1]}", "issue_id": args[1], "author": "fake"}
    rows.append({**row, "text": args[2], "created_at": now})
    return rows[-1]


_COMMANDS = {
    "label": lambda args, db, now: _label(args, db),
    "dep": lambda args, db, now: _dep(args, db),
    "comment": _comment,
}


def fake_links(args: list[str], db: dict, now: str) -> dict | list:
    """label, dep and comment for the fake record."""
    return _COMMANDS[args[0]](args, db, now)
