import pytest

from board_decide.board_decide import board_decide
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


def test_yes_closes_validation(fake_bd):
    iid = _intent()
    vid = _validation(iid)
    result = board_decide(iid, "yes", "")
    assert result == {"intent": iid, "validation": vid, "state": "done"}
    shown = _show(vid)
    assert "state:done" in shown["labels"] and shown["assignee"] == "board"
    assert "state:done" in record_run(["show", iid])[0]["labels"]


def test_no_reopens_with_reason(fake_bd):
    iid = _intent()
    vid = _validation(iid)
    assert board_decide(iid, "no", "missing X")["state"] == "reopened"
    shown = _show(vid)
    assert "state:reopened" in shown["labels"]
    assert shown.get("comment_count", len(shown.get("comments", []))) >= 1


def test_no_without_reason_rejected(fake_bd):
    iid = _intent()
    _validation(iid)
    with pytest.raises(ValueError):
        board_decide(iid, "no", "")


def test_bad_decision_rejected(fake_bd):
    iid = _intent()
    _validation(iid)
    with pytest.raises(ValueError):
        board_decide(iid, "maybe", "")


def test_no_validation_raises(fake_bd):
    with pytest.raises(ValueError):
        board_decide(_intent(), "yes", "")


def _proposal_in_cwd(fake_bd):
    import subprocess

    (fake_bd / "roles").mkdir()
    (fake_bd / "roles" / "x.md").write_text("one" + NL + "two" + NL, encoding="utf-8")
    who = ["-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", *who, "commit", "-q", "-m", "base"], check=True)
    sid = record_run(["create", "S", "-t", "task", "-l", "kind:story,state:done"])["id"]
    labels = "kind:proposal,state:checking"
    args = ["create", "P", "-t", "task", "-l", labels, "--parent", sid]
    pid = record_run(args)["id"]
    diff = NL.join(["--- a/roles/x.md", "+++ b/roles/x.md", "@@ -1,2 +1,2 @@", " one"])
    diff += NL + "-two" + NL + "+three" + NL
    head = NL.join(["page: none", "target: roles/x.md", "care: low", "---", ""])
    sheet = fake_bd / "sheet.md"
    sheet.write_text(head + diff, encoding="utf-8")
    record_run(["update", pid, "--body-file", str(sheet)])
    return pid


def test_proposal_yes_applies(fake_bd):
    pid = _proposal_in_cwd(fake_bd)
    result = board_decide(pid, "yes", "")
    assert result["state"] == "done" and result["target"] == "roles/x.md"
    text = (fake_bd / "roles" / "x.md").read_text(encoding="utf-8")
    assert text == "one" + NL + "three" + NL


def test_proposal_no_reopens(fake_bd):
    pid = _proposal_in_cwd(fake_bd)
    assert board_decide(pid, "no", "not yet")["state"] == "reopened"
    text = (fake_bd / "roles" / "x.md").read_text(encoding="utf-8")
    assert text == "one" + NL + "two" + NL
