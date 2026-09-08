from log_append.log_append import log_append
from prune.prune import prune
from puller_pids.puller_pids import puller_pids
from record_add_note.record_add_note import record_add_note
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_set_state.record_set_state import record_set_state
from release_dead_claims.release_dead_claims import release_dead_claims

_OWN = ("leftover_files: ", "no_record_item: ")


def _log_releases(released: list[str], claim_by: dict) -> None:
    for item_id in released:
        log_append(
            dict(
                item=item_id,
                gate="Housekeep",
                rule="released dead claim",
                inputs=claim_by[item_id],
                state="ready",
                tokens=0,
                seconds=0,
                actor="supervisor",
            )
        )


def _open_findings(graph: dict) -> dict:
    notes = (i for i in graph.values() if i["kind"] == "note" and i["state"] != "done")
    own = (
        i for i in notes if i["owner"] == "supervisor" and i["title"].startswith(_OWN)
    )
    return {(i["parent"], i["title"]): i["id"] for i in own}


def housekeep(repo: str) -> dict:
    """One housekeeping pass for the Supervisor.

    Claims held by pullers that no longer run are released. Every prune
    finding with a parent becomes a note under it, once. A finding note the
    Supervisor raised earlier whose condition is gone is closed by the
    Supervisor itself, so nobody pays to dismiss a stale finding. For each
    released claim a Housekeep log event is appended naming the released
    item and the original claim that was broken.
    Returns {'released', 'notes', 'cleared', 'unraised'}.
    """
    graph = record_graph()
    claim_by = {item_id: item["claimed_by"] for item_id, item in graph.items()}
    released = release_dead_claims(graph, puller_pids())
    _log_releases(released, claim_by)
    seen = {(i["parent"], i["title"]) for i in graph.values() if i["kind"] == "note"}
    own, current = _open_findings(graph), set()
    notes, unraised = [], []
    for finding in prune(graph, repo):
        key = (finding["parent"], f"{finding['rule']}: {finding['target']}")
        current.add(key)
        if key[0] is None:
            unraised.append(finding)
        elif key not in seen:
            notes.append(record_create_item("note", key[1], "supervisor", key[0])["id"])
            seen.add(key)
    cleared = [note_id for key, note_id in own.items() if key not in current]
    for note_id in cleared:
        record_add_note(
            note_id, "cleared by the Supervisor: the finding no longer holds"
        )
        record_set_state(note_id, "done")
    return dict(released=released, notes=notes, cleared=cleared, unraised=unraised)
