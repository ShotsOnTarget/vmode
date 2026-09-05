import pytest

from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run

_KINDS = ("story", "code", "test", "verification", "validation", "proposal")


def _mk(kind, owner="alice", parent=None):
    return record_create_item(kind, "t", owner, parent)


def test_owner_is_label_not_assignee(bd_repo):
    shown = record_run(["show", _mk("intent")["id"]])[0]
    assert "owner:alice" in shown["labels"] and not shown.get("assignee")


def test_each_kind_creates(bd_repo):
    intent = _mk("intent")
    assert intent["kind"] == "intent" and intent["id"]
    for kind in _KINDS:
        item = _mk(kind, parent=intent["id"])
        assert item["kind"] == kind and item["id"]


def test_bad_kind_rejected(bd_repo, monkeypatch):
    called = []
    monkeypatch.setattr(
        "record_create_item.record_create_item.record_run",
        lambda a: called.append(1) or {"id": "x"},
    )
    with pytest.raises(ValueError):
        _mk("bug", parent="p")
    assert called == []


def test_no_owner_rejected(bd_repo):
    with pytest.raises(ValueError):
        _mk("story", owner="", parent="p")


def test_no_parent_rejected(bd_repo):
    with pytest.raises(ValueError):
        _mk("story")


def test_intent_needs_no_parent(bd_repo):
    item = _mk("intent")
    assert item["kind"] == "intent" and item["id"]


def test_child_does_not_inherit_kind(bd_repo):
    story = _mk("story", parent=_mk("intent")["id"])
    labels = record_run(["show", story["id"]])[0]["labels"]
    assert "kind:story" in labels and "kind:intent" not in labels


def test_right_side_uses_validates(bd_repo):
    code = _mk("code", parent=_mk("intent")["id"])
    shown = record_run(["show", _mk("test", parent=code["id"])["id"]])[0]
    deps = shown["dependencies"]
    assert shown.get("parent") is None
    assert any(
        d["id"] == code["id"] and d["dependency_type"] == "validates" for d in deps
    )


def test_proposal_is_left_side(bd_repo):
    story = _mk("story", parent=_mk("intent")["id"])
    prop = _mk("proposal", parent=story["id"])
    assert record_run(["show", prop["id"]])[0]["parent"] == story["id"]


def test_note_created_with_parent(bd_repo):
    parent_id = _mk("intent")["id"]
    item = record_create_item("note", "saw X", "supervisor", parent=parent_id)
    assert item["kind"] == "note"
    assert item["parent"] == parent_id
    assert item["state"] == "waiting"
    labels = record_run(["show", item["id"]])[0]["labels"]
    assert "kind:note" in labels


def test_note_without_parent_rejected(bd_repo):
    with pytest.raises(ValueError):
        record_create_item("note", "saw X", "supervisor", parent=None)
