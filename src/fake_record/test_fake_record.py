import json

import pytest

from fake_record.fake_record import fake_record

# Key sets captured from bd 1.0 on 2026-09-05 (scratch database); the fake must
# answer with at least these keys so code written against the real record works.
SHOW_KEYS = {
    "id",
    "title",
    "description",
    "status",
    "priority",
    "issue_type",
    "assignee",
    "owner",
    "created_at",
    "labels",
    "dependencies",
    "dependents",
    "comments",
    "parent",
}
LIST_KEYS = {
    "id",
    "title",
    "status",
    "issue_type",
    "labels",
    "dependencies",
    "parent",
    "comment_count",
}
CREATE_KEYS = {
    "id",
    "title",
    "status",
    "priority",
    "issue_type",
    "owner",
    "created_at",
    "created_by",
    "updated_at",
}
EVENT_KEYS = {"event_kind", "actor", "target", "payload"}


@pytest.fixture(autouse=True)
def reset():
    fake_record(["__reset__"])


def _intent():
    return fake_record(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,state:waiting",
            "--no-inherit-labels",
        ]
    )


def test_create_shape_and_child_ids():
    intent = _intent()
    assert intent.keys() >= CREATE_KEYS and intent["issue_type"] == "epic"
    story = fake_record(
        ["create", "S", "-t", "task", "--parent", intent["id"], "-l", "kind:story"]
    )
    assert story["id"] == intent["id"] + ".1"


def test_show_and_list_shapes():
    iid = _intent()["id"]
    sid = fake_record(["create", "S", "-t", "task", "--parent", iid])["id"]
    shown = fake_record(["show", sid])[0]
    assert shown.keys() >= SHOW_KEYS and shown["parent"] == iid
    assert shown["dependencies"][0]["dependency_type"] == "parent-child"
    listed = fake_record(["list", "--all"])
    assert all(row.keys() >= LIST_KEYS for row in listed)
    assert listed[1]["dependencies"][0] == {
        "issue_id": sid,
        "depends_on_id": iid,
        "type": "parent-child",
    }


def test_list_filters():
    iid = _intent()["id"]
    fake_record(["update", iid, "-s", "closed"])
    assert fake_record(["list"]) == []
    assert len(fake_record(["list", "--all"])) == 1
    fake_record(
        [
            "create",
            "e",
            "--type",
            "event",
            "--event-actor",
            "a",
            "--event-category",
            "built",
            "--event-target",
            iid,
            "--event-payload",
            "{}",
        ]
    )
    assert len(fake_record(["list", "--all", "--exclude-type", "event"])) == 1
    assert len(fake_record(["list", "--all", "--type", "event"])) == 1


def test_event_shape():
    iid = _intent()["id"]
    payload = json.dumps({"tokens": 3})
    event = fake_record(
        [
            "create",
            "Built: pass",
            "--type",
            "event",
            "--event-actor",
            "sup",
            "--event-category",
            "built",
            "--event-target",
            iid,
            "--event-payload",
            payload,
        ]
    )
    assert event.keys() >= EVENT_KEYS and event["issue_type"] == "event"
    assert fake_record(["show", event["id"]])[0]["payload"] == payload


def test_labels_deps_comments_claim():
    iid = _intent()["id"]
    cid = fake_record(
        [
            "create",
            "w code",
            "-t",
            "task",
            "--parent",
            iid,
            "-l",
            "kind:code,state:waiting",
        ]
    )["id"]
    tid = fake_record(
        ["create", "w test", "-t", "task", "--parent", iid, "-l", "kind:test"]
    )["id"]
    assert fake_record(["label", "add", cid, "retry:1"]) == [
        {"issue_id": cid, "label": "retry:1", "status": "added"}
    ]
    assert "retry:1" in fake_record(["label", "list", cid])
    fake_record(["label", "remove", cid, "retry:1"])
    assert "retry:1" not in fake_record(["label", "list", cid])
    dep = fake_record(["dep", "add", tid, cid, "-t", "validates"])
    assert dep == {
        "depends_on_id": cid,
        "issue_id": tid,
        "status": "added",
        "type": "validates",
    }
    fake_record(["dep", "add", cid, "--blocked-by", tid])
    with pytest.raises(ValueError):
        fake_record(["dep", "add", cid, iid, "-t", "validates"])
    fake_record(["comment", cid, "usage: {}"])
    assert fake_record(["comments", cid])[0]["text"] == "usage: {}"
    fake_record(["update", cid, "--claim", "--actor", "b-1"])
    with pytest.raises(ValueError):
        fake_record(["update", cid, "--claim", "--actor", "b-2"])
    assert fake_record(["show", cid])[0]["assignee"] == "b-1"
    fake_record(["update", cid, "-a", ""])
    assert fake_record(["show", cid])[0]["assignee"] is None
    assert fake_record(["delete", tid, "--force"])["deleted"] == tid
