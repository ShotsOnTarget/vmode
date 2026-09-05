import pytest

from log_entry_check.log_entry_check import log_entry_check


def _entry(**overrides):
    entry = {
        "item": "vm-xyz",
        "gate": "Built",
        "rule": "rule1",
        "inputs": {"a": 1},
        "state": "done",
        "tokens": 10,
        "seconds": 1.5,
        "actor": "builder",
    }
    entry.update(overrides)
    return entry


def test_valid_returns_none():
    assert log_entry_check(_entry()) is None


def test_missing_key_raises():
    entry = _entry()
    del entry["actor"]

    with pytest.raises(ValueError):
        log_entry_check(entry)


def test_extra_key_raises():
    with pytest.raises(ValueError):
        log_entry_check(_entry(extra="nope"))


def test_bool_tokens_raises():
    with pytest.raises(ValueError):
        log_entry_check(_entry(tokens=True))


def test_negative_seconds_raises():
    with pytest.raises(ValueError):
        log_entry_check(_entry(seconds=-1))
