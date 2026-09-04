import pytest

from record_run.record_run import RecordError, record_run
from record_set_owner.record_set_owner import record_set_owner


def test_owner_changes(bd_repo):
    created = record_run(
        ["create", "hello", "-l", "owner:builder-1", "--no-inherit-labels"]
    )
    item = created[0] if isinstance(created, list) else created
    assignee_before = item.get("assignee")

    result = record_set_owner(item["id"], "builder-2")

    assert result == {"id": item["id"], "owner": "builder-2"}
    shown = record_run(["show", item["id"]])
    shown_item = shown[0] if isinstance(shown, list) else shown
    labels = shown_item.get("labels", [])
    assert "owner:builder-2" in labels
    assert "owner:builder-1" not in labels
    assert shown_item.get("assignee") == assignee_before


def test_empty_owner_rejected(bd_repo):
    created = record_run(["create", "hello", "--no-inherit-labels"])
    item = created[0] if isinstance(created, list) else created

    with pytest.raises(ValueError):
        record_set_owner(item["id"], "")


def test_unknown_raises(bd_repo):
    with pytest.raises(RecordError):
        record_set_owner("vm-none", "builder-2")
