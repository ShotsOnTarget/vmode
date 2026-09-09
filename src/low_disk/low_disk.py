import shutil

from log_append.log_append import log_append

_LIMIT_GB = 2.0


def low_disk(repo: str, graph: dict) -> float | None:
    """Say when the repo's drive is short of room, where a person will see it.

    Inputs: repo, a path on the drive to measure; graph, the record graph.
    Outputs: the free gigabytes, rounded to one place, when under two
    gigabytes, else None. Side effects: when short, one Housekeep log event
    with rule low_disk naming the free space, hung on the first open Intent
    in the graph (an event needs an item; an open Intent is what the Board
    looks at). The drive filled unseen on 2026-09-09 and every record write
    failed for forty minutes before anyone knew.
    """
    free = shutil.disk_usage(repo).free / 2**30
    if free >= _LIMIT_GB:
        return None
    intent = next(
        (i for i in graph.values() if i["kind"] == "intent" and i["state"] != "done"),
        None,
    )
    if intent is not None:
        log_append(
            dict(
                item=intent["id"],
                gate="Housekeep",
                rule="low_disk",
                inputs=f"{free:.1f} GB free",
                state=intent["state"],
                tokens=0,
                seconds=0,
                actor="supervisor",
            )
        )
    return round(free, 1)
