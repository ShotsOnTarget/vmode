from cost_rollup.cost_rollup import cost_rollup
from log_append.log_append import log_append
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _id(created):
    return created[0]["id"] if isinstance(created, list) else created["id"]


def _mk(title, **kw):
    args = ["create", title, "-a", "me", "--no-inherit-labels"]
    for k, v in kw.items():
        args += [k, v]
    return _id(record_run(args))


def _event(item, tokens):
    log_append(
        {
            "item": item,
            "gate": "Built",
            "rule": "r",
            "inputs": "i",
            "state": "s",
            "tokens": tokens,
            "seconds": 0,
            "actor": "builder",
        }
    )


def test_sums_subtree(fake_bd):
    intent = _mk("intent1")
    story = _mk("story1", **{"--parent": intent})
    code = _mk("code1", **{"--parent": story})
    _event(code, 10)
    _event(story, 20)

    result = cost_rollup(intent, record_graph())

    assert result["tokens"] == 30
    assert result["runs"] == 2


def test_negative_is_zero(fake_bd):
    item = _mk("item1")
    _event(item, -1)

    result = cost_rollup(item, record_graph())

    assert result["tokens"] == 0
    assert result["runs"] == 1


def test_no_events_zero(fake_bd):
    item = _mk("item1")

    result = cost_rollup(item, record_graph())

    assert result == {"item": item, "tokens": 0, "seconds": 0.0, "runs": 0}
