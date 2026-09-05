import pytest
from record_set_checklist.record_set_checklist import record_set_checklist

from record_run.record_run import record_run


def _item():
    created = record_run(["create", "hello", "--no-inherit-labels"])
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def test_checklist_reads_back(fake_bd):
    item_id = _item()
    items = ["first item [testing]", "second item [looking]"]

    record_set_checklist(item_id, items)

    criteria = record_run(["show", item_id])[0]["acceptance_criteria"]
    assert criteria.startswith("1. ")
    assert "first item [testing]" in criteria
    assert "second item [looking]" in criteria


def test_missing_method_rejected(fake_bd):
    item_id = _item()

    with pytest.raises(ValueError):
        record_set_checklist(item_id, ["no method here"])


def test_empty_rejected(fake_bd):
    item_id = _item()

    with pytest.raises(ValueError):
        record_set_checklist(item_id, [])
