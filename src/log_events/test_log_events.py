import json

import pytest

from log_events.log_events import log_events


def _write(path, lines):
    path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")


def test_done_maps(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(
        path,
        [
            {
                "ts": "1",
                "item": "vm-1",
                "gate": "Ready",
                "rule": "r",
                "inputs": {},
                "state": "done",
            }
        ],
    )
    assert log_events(str(path), "vm-1") == [("checking", "gate_pass")]


def test_retry_maps(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(
        path,
        [
            {
                "ts": "1",
                "item": "vm-1",
                "gate": "Ready",
                "rule": "r",
                "inputs": {"retry": 1},
                "state": "in_progress",
            }
        ],
    )
    assert log_events(str(path), "vm-1") == [("checking", "gate_fail")]


def test_blocked_maps(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(
        path,
        [
            {
                "ts": "1",
                "item": "vm-1",
                "gate": "Ready",
                "rule": "r",
                "inputs": {},
                "state": "blocked",
            }
        ],
    )
    assert log_events(str(path), "vm-1") == [("checking", "gate_fail")]


def test_other_item_skipped(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(
        path,
        [
            {
                "ts": "1",
                "item": "vm-2",
                "gate": "Ready",
                "rule": "r",
                "inputs": {},
                "state": "done",
            }
        ],
    )
    assert log_events(str(path), "vm-1") == []


def test_malformed_raises(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text("not json\n", encoding="utf-8")
    with pytest.raises(ValueError):
        log_events(str(path), "vm-1")


def test_missing_file_empty(tmp_path):
    path = tmp_path / "missing.jsonl"
    assert log_events(str(path), "vm-1") == []
