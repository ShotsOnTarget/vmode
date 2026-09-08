from housekeep.housekeep import housekeep
from log_read_item.log_read_item import log_read_item
from record_run.record_run import record_run


def _claimed_item(title: str, claim: str) -> str:
    created = record_run(
        [
            "create",
            title,
            "-t",
            "task",
            "-l",
            "kind:code,state:in_progress",
            "-a",
            claim,
        ]
    )
    return created["id"]


def test_housekeep_writes_one_log_entry_per_released_claim(fake_bd):
    first = _claimed_item("w code", "builder-99999999")
    second = _claimed_item("v code", "builder-99999997")

    result = housekeep(".")

    assert first in result["released"]
    assert second in result["released"]
    assert len(log_read_item(first)) == 1
    assert len(log_read_item(second)) == 1


def test_housekeep_log_entry_names_item_and_claim(fake_bd):
    claim = "builder-99999998"
    item = _claimed_item("w code", claim)

    result = housekeep(".")

    assert item in result["released"]
    events = log_read_item(item)
    assert len(events) == 1
    assert events[0]["item"] == item
    assert events[0]["inputs"] == claim
