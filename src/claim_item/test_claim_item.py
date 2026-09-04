import pytest

from claim_item.claim_item import claim_item
from record_run.record_run import RecordError, record_run


def _make_item():
    created = record_run(
        ["create", "-l", "kind:code,state:ready", "--no-inherit-labels", "Item"]
    )
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _show(item_id):
    shown = record_run(["show", item_id])
    return shown[0] if isinstance(shown, list) else shown


def test_claims_ready_item(bd_repo):
    item_id = _make_item()

    result = claim_item(item_id, "builder-1")

    assert result == {"id": item_id, "claimed_by": "builder-1", "state": "in_progress"}
    shown = _show(item_id)
    assert shown["assignee"] == "builder-1"
    assert "state:in_progress" in shown["labels"]


def test_second_claim_raises(bd_repo):
    item_id = _make_item()
    claim_item(item_id, "builder-1")

    with pytest.raises(RecordError):
        claim_item(item_id, "builder-2")


def test_empty_actor_raises(bd_repo):
    item_id = _make_item()

    with pytest.raises(ValueError):
        claim_item(item_id, "")
