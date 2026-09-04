import pytest
from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run

_KINDS = ("intent", "story", "code", "test", "verification", "validation")

def test_each_kind_creates(bd_repo):
    intent = record_create_item("intent", "Intent title", "alice")
    assert intent["kind"] == "intent" and intent["id"]
    for kind in _KINDS:
        if kind == "intent":
            continue
        item = record_create_item(kind, f"{kind} title", "alice", intent["id"])
        assert item["kind"] == kind and item["id"]
def test_bad_kind_rejected(bd_repo, monkeypatch):
    called = []
    monkeypatch.setattr("record_create_item.record_create_item.record_run",
                         lambda a: called.append(1) or {"id": "x"})
    with pytest.raises(ValueError):
        record_create_item("bug", "title", "alice", "parent-id")
    assert called == []
def test_no_owner_rejected(bd_repo):
    with pytest.raises(ValueError):
        record_create_item("story", "title", "", "parent-id")
def test_no_parent_rejected(bd_repo):
    with pytest.raises(ValueError):
        record_create_item("story", "title", "alice", None)
def test_intent_needs_no_parent(bd_repo):
    item = record_create_item("intent", "title", "alice", None)
    assert item["kind"] == "intent" and item["id"]
def test_child_does_not_inherit_kind(bd_repo):
    intent = record_create_item("intent", "title", "alice")
    story = record_create_item("story", "title", "alice", intent["id"])
    labels = record_run(["show", story["id"]])[0]["labels"]
    assert "kind:story" in labels and "kind:intent" not in labels
def test_right_side_uses_validates(bd_repo):
    intent = record_create_item("intent", "title", "alice")
    code = record_create_item("code", "title", "alice", intent["id"])
    t = record_create_item("test", "title", "alice", code["id"])
    shown = record_run(["show", t["id"]])[0]
    assert shown.get("parent") is None
    deps = shown["dependencies"]
    assert any(d["id"] == code["id"] and d["dependency_type"] == "validates" for d in deps)
def test_proposal_is_left_side(bd_repo):
    intent = record_create_item("intent", "title", "alice")
    story = record_create_item("story", "title", "alice", intent["id"])
    prop = record_create_item("proposal", "title", "alice", story["id"])
    assert record_run(["show", prop["id"]])[0]["parent"] == story["id"]
