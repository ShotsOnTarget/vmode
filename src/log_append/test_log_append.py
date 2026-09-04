import json

import pytest

from log_append.log_append import log_append


def _entry(**o):
    b = {
        "ts": "2026-09-04T00:00:00Z",
        "item": "item1",
        "gate": "gate1",
        "rule": "rule1",
        "inputs": {"a": 1},
        "state": "ok",
        "tokens": 10,
        "seconds": 1.5,
    }
    b.update(o)
    return b


def test_append_then_readable(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry()
    log_append(str(path), entry)
    lines = path.read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0]) == entry


def test_missing_key_writes_nothing(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry()
    del entry["rule"]
    with pytest.raises(ValueError):
        log_append(str(path), entry)
    assert not path.exists()


def test_extra_key_rejected(tmp_path):
    path = tmp_path / "log.jsonl"
    with pytest.raises(ValueError):
        log_append(str(path), _entry(extra="nope"))
    assert not path.exists()


def test_three_appends_in_order(tmp_path):
    path = tmp_path / "log.jsonl"
    entries = [_entry(item=f"item{i}") for i in range(3)]
    for e in entries:
        log_append(str(path), e)
    lines = path.read_text().splitlines()
    assert [json.loads(line) for line in lines] == entries


def test_missing_tokens_rejected(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry()
    del entry["tokens"]
    with pytest.raises(ValueError):
        log_append(str(path), entry)
    assert not path.exists()


def test_unknown_tokens_allowed(tmp_path):
    path = tmp_path / "log.jsonl"
    entry = _entry(tokens=-1, seconds=0.0)
    log_append(str(path), entry)
    assert json.loads(path.read_text().splitlines()[0]) == entry
