from board_rollup.board_rollup import board_rollup


def _item(id_, kind, title, state, parent=None):
    return {
        "id": id_,
        "kind": kind,
        "title": title,
        "owner": "",
        "state": state,
        "parent": parent,
        "checks": [],
        "needs": [],
    }


def _verification_graph():
    intent = _item("i1", "intent", "Intent 1", "open")
    story = _item("s1", "story", "Story 1", "done", parent="i1")
    verifications = {
        "v1": _item("v1", "verification", "V1", "done", parent="s1"),
        "v2": _item("v2", "verification", "V2", "open", parent="s1"),
    }
    graph = {"i1": intent, "s1": story, **verifications}
    return graph


def test_reports_incomplete_verifications():
    rows = board_rollup(_verification_graph(), {})
    assert rows == [
        {
            "id": "i1",
            "title": "Intent 1",
            "state": "open",
            "care": "",
            "stories_total": 1,
            "stories_done": 1,
            "verifications_total": 2,
            "verifications_done": 1,
            "verifications_complete": False,
        }
    ]


def test_reports_all_verifications_done():
    graph = _verification_graph()
    graph["v2"]["state"] = "done"
    rows = board_rollup(graph, {})
    assert rows[0]["verifications_done"] == 2
    assert rows[0]["verifications_total"] == 2
    assert rows[0]["verifications_complete"] is True


def test_reports_no_verifications_as_incomplete():
    graph = {"i1": _item("i1", "intent", "Intent 1", "open")}
    rows = board_rollup(graph, {})
    assert rows[0]["verifications_total"] == 0
    assert rows[0]["verifications_done"] == 0
    assert rows[0]["verifications_complete"] is False
