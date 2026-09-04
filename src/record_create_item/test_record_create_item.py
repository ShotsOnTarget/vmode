import pytest
from record_create_item.record_create_item import record_create_item

_KINDS = ("intent", "story", "code", "test", "verification", "validation")


def test_each_kind_creates(bd_repo):
    intent = record_create_item("intent", "Intent title", "alice")
    assert intent["kind"] == "intent"
    assert intent["id"]

    for kind in _KINDS:
        if kind == "intent":
            continue
        item = record_create_item(kind, f"{kind} title", "alice", intent["id"])
        assert item["kind"] == kind
        assert item["id"]


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
    assert item["kind"] == "intent"
    assert item["id"]
