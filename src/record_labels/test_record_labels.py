from record_labels.record_labels import record_labels
from record_run.record_run import record_run


def test_labels_returned(bd_repo):
    item = record_run(
        ["create", "item one", "-l", "kind:code,state:ready", "--no-inherit-labels"]
    )

    result = record_labels()

    assert "kind:code" in result[item["id"]]
    assert "state:ready" in result[item["id"]]


def test_empty_record_empty(bd_repo):
    assert record_labels() == {}
