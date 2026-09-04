import json
import pytest
from log_append.log_append import log_append


def _entry(**overrides):
    base = {
        "ts": "2026-09-04T00:00:00Z", "item": "item1", "gate": "gate1",
        "rule": "rule1", "inputs": {"a": 1}, "state": "ok",
    }
    base.update(overrides)
    return base


def test_append_then_readable(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry()
    log_append(str(path), entry)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == entry


def test_missing_key_writes_nothing(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry()
    del entry["rule"]
    with pytest.raises(ValueError):
        log_append(str(path), entry)
    assert not path.exists()


def test_extra_key_rejected(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry(extra="nope")
    with pytest.raises(ValueError):
        log_append(str(path), entry)
    assert not path.exists()


def test_three_appends_in_order(tmp_path):
    path = tmp_path / "log.jsonl"
    entries = [_entry(item=f"item{i}") for i in range(3)]
    for entry in entries:
        log_append(str(path), entry)
    lines = path.read_text().splitlines()
    assert [json.loads(line) for line in lines] == entries
