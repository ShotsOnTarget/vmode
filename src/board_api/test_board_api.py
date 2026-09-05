import pytest

from board_api.board_api import board_api
from log_append.log_append import log_append
from record_run.record_run import record_run


def _intent():
    return record_run(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,state:waiting,owner:board,care:high",
            "-a",
            "board",
            "--no-inherit-labels",
        ]
    )["id"]


def _validation(iid):
    vid = record_run(
        [
            "create",
            "V",
            "-t",
            "task",
            "-l",
            "kind:validation,state:waiting",
            "-a",
            "board",
            "--no-inherit-labels",
        ]
    )["id"]
    record_run(["dep", "add", vid, iid, "-t", "validates"])
    return vid


def test_intents_has_care(fake_bd):
    iid = _intent()
    payload = board_api("intents", {}, {})
    assert any(x["id"] == iid and x["care"] == "high" for x in payload)


def test_item_fields(fake_bd):
    iid = _intent()
    payload = board_api("item", {"id": iid}, {})
    assert {
        "id",
        "kind",
        "title",
        "owner",
        "state",
        "parent",
        "sheet",
    } <= payload.keys()


def test_columns_shape(fake_bd):
    payload = board_api("columns", {}, {})
    assert {"name", "role", "wip", "in_progress", "items"} <= payload[0].keys()


def test_decide_roundtrip(fake_bd):
    iid = _intent()
    _validation(iid)
    body = {"intent": iid, "decision": "yes", "reason": ""}
    payload = board_api("decide", {}, body)
    assert payload["state"] == "done"


def _story():
    return record_run(
        [
            "create",
            "S",
            "-t",
            "epic",
            "-l",
            "kind:story,state:waiting",
            "-a",
            "board",
            "--no-inherit-labels",
        ]
    )["id"]


def test_release_moves_ready(fake_bd):
    iid = _intent()
    board_api("release", {}, {"id": iid})
    labels = record_run(["show", iid])[0]["labels"]
    assert "state:ready" in labels


def test_release_rejects_non_intent(fake_bd):
    sid = _story()
    with pytest.raises(ValueError):
        board_api("release", {}, {"id": sid})


def test_timeline_json(fake_bd):
    iid = _intent()
    log_append(
        {
            "item": iid,
            "gate": "Board",
            "rule": "released",
            "inputs": {},
            "state": "ready",
            "tokens": 0,
            "seconds": 0.0,
            "actor": "board",
        }
    )
    payload = board_api("timeline", {"id": iid}, {})
    assert isinstance(payload, list) and len(payload) == 1
    assert payload[0]["item"] == iid


def test_unknown_name_raises(fake_bd):
    with pytest.raises(KeyError):
        board_api("nope", {}, {})
