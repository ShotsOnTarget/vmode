import pytest

from board_tree.board_tree import board_tree


def _graph():
    return {
        "intent1": {
            "id": "intent1",
            "kind": "intent",
            "title": "I",
            "owner": "o",
            "state": "open",
            "parent": None,
            "checks": [],
            "needs": [],
        },
        "story1": {
            "id": "story1",
            "kind": "story",
            "title": "S",
            "owner": "o",
            "state": "open",
            "parent": "intent1",
            "checks": [],
            "needs": [],
        },
        "code1": {
            "id": "code1",
            "kind": "code",
            "title": "C",
            "owner": "o",
            "state": "open",
            "parent": "story1",
            "checks": [],
            "needs": [],
        },
    }


def test_both_keys():
    graph = _graph()
    result = board_tree("code1", graph)
    assert len(result["back"]) == 3
    assert result["forward"]["children"] == []


def test_intent_forward():
    graph = _graph()
    result = board_tree("intent1", graph)
    assert len(result["forward"]["children"]) == 1


def test_unknown_raises():
    graph = _graph()
    with pytest.raises(ValueError):
        board_tree("nope", graph)
