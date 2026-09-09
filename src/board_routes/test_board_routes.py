from board_routes.board_routes import board_routes
from record_create_item.record_create_item import record_create_item
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


def _story():
    iid = _intent()
    sid = record_run(
        [
            "create",
            "S",
            "-t",
            "task",
            "-l",
            "kind:story,state:ready",
            "-a",
            "board",
            "--parent",
            iid,
            "--no-inherit-labels",
        ]
    )["id"]
    cid = record_run(
        [
            "create",
            "C",
            "-t",
            "task",
            "-l",
            "kind:code,state:done",
            "-a",
            "board",
            "--parent",
            sid,
            "--no-inherit-labels",
        ]
    )["id"]
    tid = record_run(
        [
            "create",
            "T",
            "-t",
            "task",
            "-l",
            "kind:test,state:done",
            "-a",
            "board",
            "--no-inherit-labels",
        ]
    )["id"]
    record_run(["dep", "add", tid, cid, "-t", "validates"])
    return sid


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


def test_root_is_html():
    status, content_type, payload = board_routes("GET", "/", {}, {})
    assert status == 200
    assert content_type == "text/html"
    assert payload.lower().startswith("<!doctype html>")


def test_columns_is_html():
    status, content_type, payload = board_routes("GET", "/columns", {}, {})
    assert status == 200
    assert "/api/columns" in payload


def test_intents_json(fake_bd):
    iid = _intent()
    status, content_type, payload = board_routes("GET", "/api/intents", {}, {})
    assert status == 200
    assert any(x["id"] == iid and x["care"] == "high" for x in payload)


def test_columns_json(fake_bd):
    status, content_type, payload = board_routes("GET", "/api/columns", {}, {})
    assert status == 200
    assert {"name", "role", "wip", "in_progress", "items"} <= payload[0].keys()


def test_decide_roundtrip(fake_bd):
    iid = _intent()
    _validation(iid)
    body = {"intent": iid, "decision": "yes", "reason": ""}
    status, content_type, payload = board_routes("POST", "/api/decide", {}, body)
    assert status == 200
    assert payload["state"] == "done"


def test_item_json(fake_bd):
    iid = _intent()
    status, content_type, payload = board_routes("GET", "/api/item", {"id": iid}, {})
    assert status == 200
    assert {
        "id",
        "kind",
        "title",
        "owner",
        "state",
        "parent",
        "sheet",
    } <= payload.keys()


def test_timeline_json(fake_bd):
    iid = _intent()
    status, _, payload = board_routes("GET", "/api/timeline", {"id": iid}, {})
    assert status == 200 and payload == []


def test_unknown_404():
    status, content_type, payload = board_routes("GET", "/nope", {}, {})
    assert status == 404


def test_bad_request_400(fake_bd):
    status, content_type, payload = board_routes(
        "GET", "/api/tree", {"id": "vm-none"}, {}
    )
    assert status == 400
    assert "error" in payload


def test_status_json(fake_bd):
    sid = _story()
    status, content_type, payload = board_routes("GET", "/api/status", {"id": sid}, {})
    assert status == 200
    assert content_type == "application/json"
    assert set(payload.keys()) == {"id", "state", "jobs", "runs"}


def test_open_questions_json(fake_bd):
    nid = record_create_item("note", "open question", "architect", parent=_story())[
        "id"
    ]
    status, content_type, payload = board_routes(
        "GET", "/api/open_questions", {"hours": "0"}, {}
    )
    assert status == 200
    assert content_type == "application/json"
    assert nid in [q["id"] for q in payload]
