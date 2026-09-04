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


def test_counts_stories():
    graph = {
        "i1": _item("i1", "intent", "Intent 1", "open"),
        "s1": _item("s1", "story", "Story 1", "done", parent="i1"),
        "s2": _item("s2", "story", "Story 2", "done", parent="i1"),
        "s3": _item("s3", "story", "Story 3", "open", parent="i1"),
    }
    rows = board_rollup(graph, {})
    assert rows == [
        {
            "id": "i1",
            "title": "Intent 1",
            "state": "open",
            "care": "",
            "stories_total": 3,
            "stories_done": 2,
        }
    ]


def test_care_passthrough():
    graph = {"i1": _item("i1", "intent", "Intent 1", "open")}
    rows = board_rollup(graph, {"i1": "high"})
    assert rows[0]["care"] == "high"
    rows2 = board_rollup(graph, {})
    assert rows2[0]["care"] == ""


def test_no_intents_empty():
    graph = {"s1": _item("s1", "story", "Story 1", "open")}
    assert board_rollup(graph, {}) == []


def test_id_order():
    graph = {
        "vm-b": _item("vm-b", "intent", "B", "open"),
        "vm-a": _item("vm-a", "intent", "A", "open"),
    }
    rows = board_rollup(graph, {})
    assert [r["id"] for r in rows] == ["vm-a", "vm-b"]
