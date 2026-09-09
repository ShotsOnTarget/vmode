from record_set_state.record_set_state import record_set_state

# what each parent kind advances on: its children of these kinds, all done
_CHILDREN = {"story": ("code", "test"), "intent": ("story",)}
# the states a parent may be in to advance; a claimed parent is someone's
_FROM = {"story": ("waiting", "ready"), "intent": ("in_progress",)}


def _ripe(item: dict, graph: dict) -> bool:
    kinds = _CHILDREN.get(item["kind"])
    if not kinds or item["claimed_by"] or item["state"] not in _FROM[item["kind"]]:
        return False
    kids = [
        j for j in graph.values() if j["parent"] == item["id"] and j["kind"] in kinds
    ]
    return bool(kids) and all(kid["state"] == "done" for kid in kids)


def advance_done(graph: dict) -> list[str]:
    """Move every parent whose children are all done on to checking.

    A Story in waiting or ready whose code and test jobs are all done goes to
    checking, the Architect's column; an Intent in_progress whose Stories are
    all done goes to checking, the Board's column. Nothing moved an Intent
    before 2026-09-09; a person set it by hand. A parent with a claim, no
    children, or any child not done is left alone. Inputs: the graph as
    record_graph returns it. Outputs: the ids advanced, in graph order.
    Side effects: one record write per id advanced.
    """
    advanced = []
    for item in graph.values():
        if _ripe(item, graph):
            record_set_state(item["id"], "checking")
            advanced.append(item["id"])
    return advanced
