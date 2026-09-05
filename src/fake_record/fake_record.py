from fake_create.fake_create import fake_create
from fake_links.fake_links import fake_links
from fake_list.fake_list import fake_list
from fake_show.fake_show import fake_show
from fake_update.fake_update import fake_update

DB = {"items": {}, "deps": [], "comments": {}, "clock": 0}


def _tick() -> str:
    DB["clock"] = c = DB["clock"] + 1
    return f"2026-09-05T{c // 3600:02d}:{c // 60 % 60:02d}:{c % 60:02d}Z"


def _delete(args, db, now):
    gone = {a for a in args[1:] if not a.startswith("-")}
    for item_id in gone:
        db["items"].pop(item_id, None)
        db["comments"].pop(item_id, None)
    before, deps = len(db["deps"]), db["deps"]
    db["deps"] = [
        d for d in deps if gone.isdisjoint((d["issue_id"], d["depends_on_id"]))
    ]
    removed = before - len(db["deps"])
    return dict(deleted=min(gone), dependencies_removed=removed, references_updated=0)


def _reset(args, db, now):
    return db.update({"items": {}, "deps": [], "comments": {}, "clock": 0}) or {}


_COMMANDS = {
    "__reset__": _reset,
    "create": fake_create,
    "update": fake_update,
    "show": lambda args, db, now: fake_show(args[1], db),
    "list": lambda args, db, now: fake_list(args, db),
    "comments": lambda args, db, now: list(db["comments"].get(args[1], [])),
    "delete": _delete,
}


def fake_record(args: list[str]) -> dict | list:
    """The in-memory record: answers `bd` commands with the real shapes.

    Covers the commands the code uses; `["__reset__"]` empties it. Shapes
    were captured from bd 1.0 on 2026-09-05; the fake's tests hold them.
    """
    handler = _COMMANDS.get(args[0], fake_links)
    return handler(list(args), DB, _tick())
