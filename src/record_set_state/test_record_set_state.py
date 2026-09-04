import pytest

from record_set_state.record_set_state import record_set_state
from record_run.record_run import record_run

_STATES = (
    "waiting", "ready", "in_progress", "blocked",
    "checking", "done", "reopened",
)


def _make_item():
    item = record_run(["create", "-l", "kind:task", "-t", "task", "-a", "alice", "Item"])
    return item["id"]


def _show(item_id):
    return record_run(["show", item_id])[0]


def _state_labels(item_id):
    labels = _show(item_id)["labels"]
    return [l for l in labels if l.startswith("state:")]


def test_each_state_sets(bd_repo):
    item_id = _make_item()
    for state in _STATES:
        record_set_state(item_id, state)
        state_labels = _state_labels(item_id)
        assert state_labels == [f"state:{state}"]


def test_eighth_state_rejected(bd_repo):
    item_id = _make_item()
    with pytest.raises(ValueError):
        record_set_state(item_id, "paused")


def test_done_closes(bd_repo):
    item_id = _make_item()
    record_set_state(item_id, "done")
    assert _show(item_id)["status"] == "closed"


def test_reopened_opens(bd_repo):
    item_id = _make_item()
    record_set_state(item_id, "done")
    record_set_state(item_id, "reopened")
    assert _show(item_id)["status"] == "open"
