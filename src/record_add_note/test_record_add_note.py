import pytest

from record_add_note.record_add_note import record_add_note
from record_run.record_run import record_run


def _item(title):
    return record_run(["create", title, "-t", "task", "--no-inherit-labels"])["id"]


def test_note_added(bd_repo):
    item_id = _item("a")
    record_add_note(item_id, "hello")
    show = record_run(["show", item_id])
    row = show[0] if isinstance(show, list) else show
    has_count = row.get("comment_count") == 1
    has_list = len(row.get("comments", [])) == 1
    assert has_count or has_list


def test_empty_text_rejected(bd_repo):
    item_id = _item("b")
    with pytest.raises(ValueError):
        record_add_note(item_id, "")


def test_two_notes_two_ids(bd_repo):
    item_id = _item("c")
    first = record_add_note(item_id, "one")
    second = record_add_note(item_id, "two")
    assert first["note_id"] != second["note_id"]
