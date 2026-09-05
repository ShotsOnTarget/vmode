import pytest

from board_decide.board_decide import board_decide
from record_run.record_run import record_run


def _intent():
    return record_run(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,care:low",
            "-a",
            "alice",
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


def _show(item_id):
    return record_run(["show", item_id])[0]


def test_yes_closes_validation(bd_repo):
    iid = _intent()
    vid = _validation(iid)
    result = board_decide(iid, "yes", "")
    assert result == {"intent": iid, "validation": vid, "state": "done"}
    shown = _show(vid)
    assert "state:done" in shown["labels"] and shown["assignee"] == "board"
    assert "state:done" in record_run(["show", iid])[0]["labels"]


def test_no_reopens_with_reason(bd_repo):
    iid = _intent()
    vid = _validation(iid)
    assert board_decide(iid, "no", "missing X")["state"] == "reopened"
    shown = _show(vid)
    assert "state:reopened" in shown["labels"]
    assert shown.get("comment_count", len(shown.get("comments", []))) >= 1


def test_no_without_reason_rejected(bd_repo):
    iid = _intent()
    _validation(iid)
    with pytest.raises(ValueError):
        board_decide(iid, "no", "")


def test_bad_decision_rejected(bd_repo):
    iid = _intent()
    _validation(iid)
    with pytest.raises(ValueError):
        board_decide(iid, "maybe", "")


def test_no_validation_raises(bd_repo):
    with pytest.raises(ValueError):
        board_decide(_intent(), "yes", "")
