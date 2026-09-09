import pytest

from board_api.board_api import board_api
from log_append.log_append import log_append
from record_add_note.record_add_note import record_add_note
from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state


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


def _story_with_jobs():
    iid = _intent()
    sid = record_run(
        [
            "create",
            "S",
            "-t",
            "epic",
            "-l",
            "kind:story,state:ready",
            "-a",
            "board",
            "--no-inherit-labels",
            "--parent",
            iid,
        ]
    )["id"]
    cid = record_run(
        [
            "create",
            "widget code",
            "-t",
            "task",
            "-l",
            "kind:code,state:done",
            "-a",
            "builder",
            "--no-inherit-labels",
            "--parent",
            sid,
        ]
    )["id"]
    tid = record_run(
        [
            "create",
            "widget test",
            "-t",
            "task",
            "-l",
            "kind:test,state:done",
            "-a",
            "builder",
            "--no-inherit-labels",
            "--parent",
            sid,
        ]
    )["id"]
    record_run(["dep", "add", tid, cid, "-t", "validates"])
    return sid


def test_status_view(fake_bd):
    sid = _story_with_jobs()
    payload = board_api("status", {"id": sid}, {})
    assert {"id", "state", "jobs", "runs"} <= payload.keys()
    assert payload["id"] == sid
    assert len(payload["jobs"]) == 2


def _question_job():
    iid = _intent()
    sid = record_run(
        [
            "create",
            "widget story",
            "-t",
            "epic",
            "-l",
            "kind:story,state:ready",
            "-a",
            "board",
            "--no-inherit-labels",
            "--parent",
            iid,
        ]
    )["id"]
    jid = record_create_item("code", "widget job", "builder", parent=sid)["id"]
    return iid, sid, jid


def _note(jid, title, owner):
    return record_create_item("note", title, owner, parent=jid)["id"]


def test_open_questions_api(fake_bd):
    _, sid, jid = _question_job()

    open_note = _note(jid, "open question", "engineer")
    builder_note = _note(jid, "builder question", "builder")
    done_unanswered = _note(jid, "done without answer", "engineer")
    record_add_note(done_unanswered, "looks fine")
    record_set_state(done_unanswered, "done")

    owner_answered = _note(jid, "owner answered", "engineer")
    record_add_note(owner_answered, "answer (engineer): fixed")
    board_answered = _note(jid, "board answered", "builder")
    record_add_note(board_answered, "answer (board): agreed")
    analyst_note = _note(jid, "analyst note", "analyst")
    supervisor_note = _note(jid, "supervisor note", "supervisor")

    payload = board_api("open_questions", {"hours": 0}, {})

    returned = {q["id"] for q in payload}
    assert {open_note, builder_note, done_unanswered} <= returned
    assert returned.isdisjoint(
        {owner_answered, board_answered, analyst_note, supervisor_note}
    )
    assert all(q["story"] == sid for q in payload)
