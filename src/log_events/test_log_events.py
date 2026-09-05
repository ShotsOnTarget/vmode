import pytest

from log_append.log_append import log_append
from log_events.log_events import log_events
from record_run.record_run import record_run


def _item():
    return record_run(["create", "X", "-t", "task", "-l", "kind:code,state:waiting"])[
        "id"
    ]


def _event(item_id, gate, state, **inputs):
    log_append(
        {
            "item": item_id,
            "gate": gate,
            "rule": "r",
            "inputs": inputs,
            "state": state,
            "tokens": 0,
            "seconds": 0.0,
            "actor": "t",
        }
    )


def test_done_maps(fake_bd):
    item_id = _item()
    _event(item_id, "Built", "done", action="log_done", retries=0)
    assert log_events(item_id) == [("checking", "gate_pass")]


def test_retry_maps(fake_bd):
    item_id = _item()
    _event(item_id, "Built", "ready", action="bounce", retries=1)
    assert log_events(item_id) == [("checking", "gate_fail")]


def test_blocked_maps(fake_bd):
    item_id = _item()
    _event(item_id, "Built", "blocked", action="escalate", retries=3)
    assert log_events(item_id) == [("checking", "gate_fail")]


def test_other_item_skipped(fake_bd):
    item_id, other = _item(), _item()
    _event(other, "Built", "done", action="log_done")
    assert log_events(item_id) == []


def test_lesson_no_transition(fake_bd):
    item_id = _item()
    _event(item_id, "Lesson", "in_progress")
    assert log_events(item_id) == []


def test_missing_state_raises(fake_bd, monkeypatch):
    monkeypatch.setattr(
        "log_events.log_events.log_read_item", lambda i: [{"gate": "built"}]
    )
    with pytest.raises(ValueError):
        log_events("vm-1")
