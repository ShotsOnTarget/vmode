from proposal_sweep.proposal_sweep import proposal_sweep
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_run.record_run import record_run

GOOD = (
    "page: vm-v1d.1.8\ntarget: roles/builder/SKILL.md\ncare: low\n---\n"
    "--- a/roles/builder/SKILL.md\n+++ b/roles/builder/SKILL.md\n+ line\n"
)


def _story():
    intent = record_create_item("intent", "I", "board")
    return record_create_item("story", "S", "architect", intent["id"])["id"]


def _proposal(story, sheet, tmp_path):
    pid = record_create_item("proposal", "P", "analyst", story)["id"]
    path = tmp_path / "sheet.md"
    path.write_text(sheet, encoding="utf-8")
    record_run(["update", pid, "--body-file", str(path)])
    return pid


def test_clean_moves_to_checking(fake_bd, tmp_path):
    pid = _proposal(_story(), GOOD, tmp_path)
    assert proposal_sweep(record_graph()) == [pid]
    assert record_graph()[pid]["state"] == "checking"


def test_empty_sheet_blocked(fake_bd, tmp_path):
    pid = _proposal(_story(), "", tmp_path)
    assert proposal_sweep(record_graph()) == []
    assert record_graph()[pid]["state"] == "blocked"
    assert record_run(["comments", pid])[-1]["text"].startswith("proposal gate:")


def test_non_proposals_untouched(fake_bd):
    story = _story()
    proposal_sweep(record_graph())
    assert record_graph()[story]["state"] == "waiting"
