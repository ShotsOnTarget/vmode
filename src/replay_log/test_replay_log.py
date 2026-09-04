import json

from replay_log.replay_log import replay_log


def _write_log(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            record = {
                "gate": "Proven",
                "rule": "test",
                "ts": "2026-09-04T00:00:00+00:00",
                "inputs": {},
            }
            record.update(line)
            f.write(json.dumps(record) + "\n")


def test_retry_then_done(tmp_path):
    path = tmp_path / "log.jsonl"
    _write_log(
        path,
        [
            {"item": "X", "state": "in_progress", "inputs": {"retry": 1}},
            {"item": "X", "state": "done"},
        ],
    )
    assert replay_log(str(path), "X") == "done"


def test_three_fails_blocked(tmp_path):
    path = tmp_path / "log.jsonl"
    _write_log(
        path,
        [
            {"item": "X", "state": "in_progress", "inputs": {"retry": 1}},
            {"item": "X", "state": "in_progress", "inputs": {"retry": 2}},
            {"item": "X", "state": "in_progress", "inputs": {"retry": 3}},
            {"item": "X", "state": "blocked"},
        ],
    )
    assert replay_log(str(path), "X") == "blocked"


def test_reopen_after_done(tmp_path):
    path = tmp_path / "log.jsonl"
    _write_log(
        path,
        [
            {"item": "X", "state": "done"},
            {"item": "X", "state": "reopened"},
        ],
    )
    assert replay_log(str(path), "X") == "reopened"


def test_other_item_ignored(tmp_path):
    path = tmp_path / "log.jsonl"
    _write_log(
        path,
        [
            {"item": "Y", "state": "in_progress", "inputs": {"retry": 1}},
            {"item": "Y", "state": "done"},
        ],
    )
    assert replay_log(str(path), "X") == "waiting"


def test_real_log_item():
    assert replay_log("work/supervisor-log.jsonl", "0001-1-record_run") == "done"
