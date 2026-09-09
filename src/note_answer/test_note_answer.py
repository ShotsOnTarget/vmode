import pytest
from note_answer.note_answer import note_answer

from record_add_note.record_add_note import record_add_note
from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _job():
    intent = record_create_item("intent", "intent", "supervisor")
    return record_create_item("code", "job", "supervisor", parent=intent["id"])["id"]


def _note(job_id, owner):
    return record_create_item("note", "question", owner, parent=job_id)["id"]


def _comment_texts(note_id):
    return [c["text"] for c in record_run(["comments", note_id])]


def test_note_owner_can_answer_and_close(fake_bd):
    note_id = _note(_job(), "engineer")

    note_answer(note_id, "engineer", "fixed")

    assert _comment_texts(note_id) == ["answer (engineer): fixed"]
    assert record_show_item(note_id)["state"] == "done"


def test_board_can_answer_any_owned_note_and_close(fake_bd):
    note_id = _note(_job(), "architect")

    note_answer(note_id, "board", "agreed")

    assert _comment_texts(note_id) == ["answer (board): agreed"]
    assert record_show_item(note_id)["state"] == "done"


def test_bystander_is_refused_without_mutation(fake_bd):
    note_id = _note(_job(), "engineer")
    record_add_note(note_id, "please look")
    before = record_show_item(note_id)

    with pytest.raises(ValueError) as exc:
        note_answer(note_id, "architect", "not yours")

    assert "engineer" in str(exc.value)
    assert record_show_item(note_id)["state"] == before["state"]
    assert _comment_texts(note_id) == ["please look"]
