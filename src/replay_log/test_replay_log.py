from log_append.log_append import log_append
from record_run.record_run import record_run
from replay_log.replay_log import replay_log


def _item():
    return record_run(["create", "X", "-t", "task", "-l", "kind:code,state:waiting"])[
        "id"
    ]


def _event(item_id, state, action, retries):
    inputs = {"action": action, "retries": retries}
    log_append(
        {
            "item": item_id,
            "gate": "Built",
            "rule": "r",
            "inputs": inputs,
            "state": state,
            "tokens": 0,
            "seconds": 0.0,
            "actor": "t",
        }
    )


def test_retry_then_done(fake_bd):
    item_id = _item()
    _event(item_id, "ready", "bounce", 1)
    _event(item_id, "done", "log_done", 1)
    assert replay_log(item_id) == "done"


def test_three_fails_blocked(fake_bd):
    item_id = _item()
    for n in (1, 2, 3):
        _event(item_id, "ready", "bounce", n)
    _event(item_id, "blocked", "escalate", 3)
    assert replay_log(item_id) == "blocked"


def test_no_events_waiting(fake_bd):
    assert replay_log(_item()) == "waiting"
