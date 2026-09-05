import pytest

from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from trace_forward.trace_forward import trace_forward


def _id(created):
    return created[0]["id"] if isinstance(created, list) else created["id"]


def _mk(title, **kw):
    args = ["create", title, "-a", "me", "--no-inherit-labels"]
    for k, v in kw.items():
        args += [k, v]
    return _id(record_run(args))


def test_full_tree(fake_bd):
    intent = _mk("intent1")
    story = _mk("story1", **{"--parent": intent})
    code = _mk("code1", **{"--parent": story})
    verification = _mk("verification1")
    record_run(["dep", "add", verification, story, "-t", "validates"])
    tree = trace_forward(intent, record_graph())
    assert tree["id"] == intent
    story_node = tree["children"][0]
    assert story_node["id"] == story
    assert {c["id"] for c in story_node["children"]} == {code, verification}


def test_leaf_has_no_children(fake_bd):
    code = _mk("code1")
    assert trace_forward(code, record_graph())["children"] == []


def test_unknown_id_raises(fake_bd):
    with pytest.raises(ValueError):
        trace_forward("nope", record_graph())


def test_no_duplicate_when_child_also_checks():
    graph = {
        "story": {
            "id": "story",
            "kind": "story",
            "title": "s",
            "parent": None,
            "checks": [],
        },
        "verification": {
            "id": "verification",
            "kind": "verification",
            "title": "v",
            "parent": "story",
            "checks": ["story"],
        },
    }
    children = trace_forward("story", graph)["children"]
    assert [c["id"] for c in children] == ["verification"]
