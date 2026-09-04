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
    called = False

    def fake_run(args):
        nonlocal called
        called = True
        return {"id": "x"}
    monkeypatch.setattr(
        "record_create_item.record_create_item.record_run", fake_run
    )
    with pytest.raises(ValueError):
        record_create_item("bug", "title", "alice", "parent-id")
    assert called is False

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
    assert "kind:story" in labels
    assert "kind:intent" not in labels

def test_right_side_uses_validates(bd_repo):
    intent = record_create_item("intent", "title", "alice")
    code = record_create_item("code", "title", "alice", intent["id"])
    test_item = record_create_item("test", "title", "alice", code["id"])
    shown = record_run(["show", test_item["id"]])[0]
    assert shown.get("parent") is None
    deps = shown["dependencies"]
    assert any(
        d["depends_on_id"] == code["id"] and d["type"] == "validates"
        for d in deps
    )
