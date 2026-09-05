from log_append.log_append import log_append
from record_labels.record_labels import record_labels
from record_run.record_run import record_run


def test_labels_returned(fake_bd):
    item = record_run(
        ["create", "item one", "-l", "kind:code,state:ready", "--no-inherit-labels"]
    )

    result = record_labels()

    assert "kind:code" in result[item["id"]]
    assert "state:ready" in result[item["id"]]


def test_empty_record_empty(fake_bd):
    assert record_labels() == {}


def test_events_not_listed(fake_bd):
    item = record_run(["create", "item one"])
    event_id = log_append(
        {
            "item": item["id"],
            "gate": "Built",
            "rule": "rule1",
            "inputs": {},
            "state": "ok",
            "tokens": 1,
            "seconds": 1.0,
            "actor": "builder",
        }
    )

    result = record_labels()

    assert event_id not in result
