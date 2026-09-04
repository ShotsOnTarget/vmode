import json

import pytest

from log_read_item.log_read_item import log_read_item


def test_returns_matching_in_order(tmp_path):
    path = tmp_path / "log.jsonl"
    lines = [
        {"item": "A", "n": 1},
        {"item": "B", "n": 1},
        {"item": "A", "n": 2},
        {"item": "B", "n": 2},
        {"item": "A", "n": 3},
    ]
    path.write_text("\n".join(json.dumps(line) for line in lines) + "\n")
    result = log_read_item(str(path), "A")
    assert result == [
        {"item": "A", "n": 1},
        {"item": "A", "n": 2},
        {"item": "A", "n": 3},
    ]


def test_missing_file_returns_empty(tmp_path):
    result = log_read_item(str(tmp_path / "log.jsonl"), "A")
    assert result == []


def test_bad_line_raises(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text("not json\n")
    with pytest.raises(ValueError):
        log_read_item(str(path), "A")


def test_file_unchanged_after_read(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_bytes((json.dumps({"item": "A", "n": 1}) + "\n").encode("utf-8"))
    before = path.read_bytes()
    log_read_item(str(path), "A")
    assert before == path.read_bytes()
