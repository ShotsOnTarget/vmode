import io

import pytest

from record_run.record_run import record_run
from record_set_sheet.record_set_sheet import record_set_sheet
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


def test_em_dash_reads_back_unchanged(fake_bd):
    item_id = _item()
    text = "line one—line two"

    record_set_sheet(item_id, text)

    assert record_show_item(item_id)["sheet"] == text


def test_mixed_non_ascii_reads_back_unchanged(fake_bd):
    item_id = _item()
    text = "em—dash en–dash café"

    record_set_sheet(item_id, text)

    assert record_show_item(item_id)["sheet"] == text


def test_non_ascii_returned_dict_matches(fake_bd):
    item_id = _item()
    text = "em—dash en–dash café"

    result = record_set_sheet(item_id, text)

    assert result == {"id": item_id, "sheet": text}


def test_command_line_reads_the_sheet_from_stdin(fake_bd):
    """One argument, the id; the whole of stdin is the sheet, newlines and all."""
    from record_set_sheet.record_set_sheet import _main

    item_id = _item()
    text = "# Instruction sheet\n\n- **Job id**: x\n- **Cases**:\n  - `test_a`: works\n"

    result = _main([item_id], io.StringIO(text))

    assert result == {"id": item_id, "sheet": text}
    assert record_show_item(item_id)["sheet"] == text
    with pytest.raises(ValueError):
        _main([], io.StringIO(text))
