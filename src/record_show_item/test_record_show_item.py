import pytest

from record_run.record_run import RecordError, record_run
from record_show_item.record_show_item import record_show_item


def test_returns_fields(bd_repo):
    item = record_run(
        [
            "create",
            "title",
            "-t",
            "task",
            "-l",
            "kind:story,state:waiting,owner:alice",
            "--description",
            "do x",
            "--no-inherit-labels",
        ]
    )
    result = record_show_item(item["id"])
    assert result["kind"] == "story"
    assert result["owner"] == "alice"
    assert result["state"] == "waiting"
    assert result["parent"] == item.get("parent")
    assert result["sheet"] == "do x"


def test_unknown_raises(bd_repo):
    with pytest.raises(RecordError):
        record_show_item("vm-none")


def test_sheet_empty_when_no_description(bd_repo):
    item = record_run(
        [
            "create",
            "title",
            "-t",
            "task",
            "-l",
            "kind:story,state:waiting,owner:alice",
            "--no-inherit-labels",
        ]
    )
    result = record_show_item(item["id"])
    assert result["sheet"] == ""
