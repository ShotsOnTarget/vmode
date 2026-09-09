from board_decide.board_decide import board_decide
from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run

NL = chr(10)


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


def test_validates_over_failed_smoke_and_records_override(fake_bd):
    iid = _intent()
    _validation(iid)
    record_add_note(iid, "smoke: failed")
    result = board_decide(iid, "yes", "")
    assert result["state"] == "done"
    assert "state:done" in record_run(["show", iid])[0]["labels"]
    shown = _show(iid)
    assert any(
        "smoke: failed" in (c.get("text") or "") for c in shown.get("comments", [])
    )


def test_validates_over_skipped_smoke_and_records_override(fake_bd):
    iid = _intent()
    _validation(iid)
    record_add_note(iid, "smoke: skipped")
    result = board_decide(iid, "yes", "")
    assert result["state"] == "done"
    assert "state:done" in record_run(["show", iid])[0]["labels"]
    shown = _show(iid)
    assert any(
        "smoke: skipped" in (c.get("text") or "") for c in shown.get("comments", [])
    )


def test_no_decision_still_requires_reason_and_reopens(fake_bd):
    iid = _intent()
    _validation(iid)
    result = board_decide(iid, "no", "missing X")
    assert result["state"] == "reopened"
    assert "state:reopened" in record_run(["show", iid])[0]["labels"]


def test_no_on_a_proposal_closes_it_with_the_reason(fake_bd):
    """A refused proposal is decided: done, never reopened into the verify column."""
    pid = record_run(
        ["create", "P", "-t", "task", "-l", "kind:proposal,state:checking"]
    )["id"]
    result = board_decide(pid, "no", "already in the skill")
    assert result["state"] == "done"
    shown = _show(pid)
    assert "state:done" in shown["labels"]
    texts = [c.get("text") or "" for c in shown["comments"]]
    assert any("already in the skill" in text for text in texts)
