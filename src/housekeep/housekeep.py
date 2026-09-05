from prune.prune import prune
from puller_pids.puller_pids import puller_pids
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from release_dead_claims.release_dead_claims import release_dead_claims


def housekeep(repo: str) -> dict:
    """One housekeeping pass for the Supervisor: release dead claims, raise notes.

    Claims held by pullers that no longer run are released. Every prune
    finding with a parent becomes a note under it, unless a note with the
    same title already sits there, so a standing problem is raised once.
    Returns {'released': [ids], 'notes': [ids], 'unraised': [findings]}.
    """
    graph = record_graph()
    released = release_dead_claims(graph, puller_pids())
    existing = {
        (item["parent"], item["title"])
        for item in graph.values()
        if item["kind"] == "note"
    }
    notes, unraised = [], []
    for finding in prune(graph, repo):
        title = f"{finding['rule']}: {finding['target']}"
        parent = finding["parent"]
        if parent is None:
            unraised.append(finding)
        elif (parent, title) not in existing:
            notes.append(record_create_item("note", title, "supervisor", parent)["id"])
            existing.add((parent, title))
    return {"released": released, "notes": notes, "unraised": unraised}
