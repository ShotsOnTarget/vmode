import pytest
from record_set_sheet.record_set_sheet import record_set_sheet

from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _item():
    created = record_run(["create", "hello", "--no-inherit-labels"])
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def test_sheet_reads_back(fake_bd):
    item_id = _item()
    text = "line one\nline two"

    record_set_sheet(item_id, text)

    assert record_show_item(item_id)["sheet"] == text


def test_replaces_previous(fake_bd):
    item_id = _item()
    record_set_sheet(item_id, "first")

    record_set_sheet(item_id, "second")

    assert record_show_item(item_id)["sheet"] == "second"


def test_empty_rejected(fake_bd):
    item_id = _item()

    with pytest.raises(ValueError):
        record_set_sheet(item_id, "  ")

    assert record_show_item(item_id)["sheet"] == ""
