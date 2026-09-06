import subprocess

import pytest

from proposal_apply.proposal_apply import proposal_apply
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _repo(tmp_path):
    repo = tmp_path / "target"
    (repo / "roles").mkdir(parents=True)
    (repo / "roles" / "x.md").write_text("one\ntwo\n", encoding="utf-8")
    for args in (
        ["init", "-q"],
        ["config", "user.email", "t@t"],
        ["config", "user.name", "t"],
        ["add", "."],
        ["commit", "-q", "-m", "base"],
    ):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)
    return repo


def _proposal(sheet, tmp_path):
    intent = record_create_item("intent", "I", "board")
    story = record_create_item("story", "S", "architect", intent["id"])["id"]
    pid = record_create_item("proposal", "P", "analyst", story)["id"]
    path = tmp_path / "sheet.md"
    path.write_bytes(sheet.encode("utf-8"))
    record_run(["update", pid, "--body-file", str(path)])
    return pid


DIFF = "--- a/roles/x.md\n+++ b/roles/x.md\n@@ -1,2 +1,2 @@\n one\n-two\n+three\n"


def test_applies_and_closes(fake_bd, tmp_path):
    repo = _repo(tmp_path)
    pid = _proposal("page: none\ntarget: roles/x.md\ncare: low\n---\n" + DIFF, tmp_path)
    out = proposal_apply(pid, str(repo), "2026-09-05")
    assert (repo / "roles" / "x.md").read_text(encoding="utf-8") == "one\nthree\n"
    assert out["target"] == "roles/x.md" and out["commit"]
    assert record_graph()[pid]["state"] == "done"
    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"], cwd=repo, capture_output=True, text=True
    ).stdout
    assert pid in log


def test_bad_diff_changes_nothing(fake_bd, tmp_path):
    repo = _repo(tmp_path)
    bad = DIFF.replace("-two", "-nine")
    pid = _proposal("page: none\ntarget: roles/x.md\ncare: low\n---\n" + bad, tmp_path)
    with pytest.raises(ValueError):
        proposal_apply(pid, str(repo), "2026-09-05")
    assert (repo / "roles" / "x.md").read_text(encoding="utf-8") == "one\ntwo\n"
    assert record_graph()[pid]["state"] != "done"


def test_not_proposal_raises(fake_bd, tmp_path):
    intent = record_create_item("intent", "I", "board")["id"]
    with pytest.raises(ValueError):
        proposal_apply(intent, str(tmp_path), "2026-09-05")


def test_crlf_sheet_applies(fake_bd, tmp_path):
    repo = _repo(tmp_path)
    nl, crlf_end = chr(10), chr(13) + chr(10)
    head = nl.join(["page: none", "target: roles/x.md", "care: low", "---", ""])
    crlf = (head + DIFF).replace(nl, crlf_end)
    pid = _proposal(crlf, tmp_path)
    proposal_apply(pid, str(repo), "2026-09-06")
    text = (repo / "roles" / "x.md").read_text(encoding="utf-8")
    assert text == "one" + nl + "three" + nl
