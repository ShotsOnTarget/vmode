import json

import pytest

from log_append.log_append import log_append
from record_run.record_run import record_run


def _target():
    created = record_run(["create", "target item"])
    created = created[0] if isinstance(created, list) else created
    return created["id"]


def _entry(item, **overrides):
    entry = {
        "item": item,
        "gate": "Built",
        "rule": "rule1",
        "inputs": {"a": 1},
        "state": "ok",
        "tokens": 10,
        "seconds": 1.5,
        "actor": "builder",
    }
    entry.update(overrides)
    return entry


def test_creates_event(bd_repo):
    target = _target()

    event_id = log_append(_entry(target))

    assert event_id.startswith("vm-")
    shown = record_run(["show", event_id])[0]
    assert shown["issue_type"] == "event"
    assert shown["event_kind"] == "built"


def test_missing_key_rejected(bd_repo):
    target = _target()
    entry = _entry(target)
    del entry["actor"]

    with pytest.raises(ValueError):
        log_append(entry)

    assert record_run(["list", "--type", "event"]) == []


def test_extra_key_rejected(bd_repo):
    target = _target()
    entry = _entry(target, extra="nope")

    with pytest.raises(ValueError):
        log_append(entry)


def test_payload_roundtrip(bd_repo):
    target = _target()
    entry = _entry(target, tokens=42)

    event_id = log_append(entry)

    shown = record_run(["show", event_id])[0]
    assert json.loads(shown["payload"])["tokens"] == 42
