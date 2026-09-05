import pytest

from board_api.board_api import board_api
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


def test_intents_has_care(bd_repo):
    iid = _intent()
    payload = board_api("intents", {}, {})
    assert any(x["id"] == iid and x["care"] == "high" for x in payload)


def test_item_fields(bd_repo):
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


def test_columns_shape(bd_repo):
    payload = board_api("columns", {}, {})
    assert {"name", "role", "wip", "in_progress", "items"} <= payload[0].keys()


def test_decide_roundtrip(bd_repo):
    iid = _intent()
    _validation(iid)
    body = {"intent": iid, "decision": "yes", "reason": ""}
    payload = board_api("decide", {}, body)
    assert payload["state"] == "done"


def test_unknown_name_raises(bd_repo):
    with pytest.raises(KeyError):
        board_api("nope", {}, {})
