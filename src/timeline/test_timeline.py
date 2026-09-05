import pytest

from log_append.log_append import log_append
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from timeline.timeline import timeline


def _id(created):
    return created[0]["id"] if isinstance(created, list) else created["id"]


def _mk(title, **kw):
    args = ["create", title, "-a", "me", "--no-inherit-labels"]
    for k, v in kw.items():
        args += [k, v]
    return _id(record_run(args))


def _event(item, tokens=1):
    return {
        "item": item,
        "gate": "Built",
        "rule": "r",
        "inputs": "i",
        "state": "s",
        "tokens": tokens,
        "seconds": 0,
        "actor": "builder",
    }


def test_subtree_events_in_order(fake_bd):
    intent = _mk("intent1")
    story = _mk("story1", **{"--parent": intent})
    code = _mk("code1", **{"--parent": story})

    log_append(_event(code))
    log_append(_event(intent))
    log_append(_event(story))

    result = timeline(intent, record_graph())

    assert [e["item"] for e in result] == [code, intent, story]


def test_leaf_only_own(fake_bd):
    intent = _mk("intent1")
    story = _mk("story1", **{"--parent": intent})
    code = _mk("code1", **{"--parent": story})

    log_append(_event(code))
    log_append(_event(intent))
    log_append(_event(story))

    result = timeline(code, record_graph())

    assert len(result) == 1
    assert result[0]["item"] == code


def test_unknown_raises(fake_bd):
    with pytest.raises(ValueError):
        timeline("nope", record_graph())
