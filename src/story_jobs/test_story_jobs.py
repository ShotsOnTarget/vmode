import pytest

from story_jobs.story_jobs import story_jobs


def _item(kind, parent=None, checks=None):
    return {
        "id": "",
        "kind": kind,
        "title": "",
        "owner": "",
        "state": "",
        "parent": parent,
        "checks": checks or [],
        "needs": [],
    }


def test_has_intent_true():
    graph = {
        "i1": _item("intent", parent=None),
        "s1": _item("story", parent="i1"),
    }
    result = story_jobs("s1", graph)
    assert result["has_intent"] is True


def test_has_intent_false():
    graph = {
        "s1": _item("story", parent=None),
    }
    result = story_jobs("s1", graph)
    assert result["has_intent"] is False


def test_code_and_tests():
    graph = {
        "s1": _item("story", parent=None),
        "c1": _item("code", parent="s1"),
        "t1": _item("test", parent="s1", checks=["c1"]),
    }
    result = story_jobs("s1", graph)
    assert result["code"] == ["c1"]
    assert result["tests"] == {"c1": ["t1"]}


def test_code_without_test_empty_list():
    graph = {
        "s1": _item("story", parent=None),
        "c1": _item("code", parent="s1"),
    }
    result = story_jobs("s1", graph)
    assert result["tests"] == {"c1": []}


def test_unknown_raises():
    graph = {
        "s1": _item("story", parent=None),
    }
    with pytest.raises(ValueError):
        story_jobs("unknown", graph)
