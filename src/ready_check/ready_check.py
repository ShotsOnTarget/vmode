_OPEN = ("ready", "reopened", "in_progress", "checking")


def ready_check(item_id: str, graph: dict) -> list[str]:
    """Reasons a code or test job must not become Ready; [] when it may.

    duplicate_function: another job with the same title exists, so the
    function would have two folders or two histories. folder_conflict:
    another open job (ready, reopened, in progress, checking) works the same
    folder, so two Builders would collide. Other kinds always pass.
    """
    item = graph.get(item_id)
    if item is None:
        raise ValueError(f"unknown item: {item_id}")
    if item["kind"] not in ("code", "test"):
        return []
    folder = item["title"].rsplit(" ", 1)[0]
    others = [
        o
        for oid, o in graph.items()
        if oid != item_id and o["kind"] in ("code", "test")
    ]
    reasons = set()
    if any(o["title"] == item["title"] for o in others):
        reasons.add("duplicate_function")
    same_folder = (o for o in others if o["title"].rsplit(" ", 1)[0] == folder)
    if any(o["state"] in _OPEN and o["title"] != item["title"] for o in same_folder):
        reasons.add("folder_conflict")
    return sorted(reasons)
