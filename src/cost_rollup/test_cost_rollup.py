import json

from cost_rollup.cost_rollup import cost_rollup


def _write(path, lines):
    with open(path, "w") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")


def test_intent_equals_sum_of_stories(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(path, [
        {"item": "0001-1-a-code", "tokens": 10, "seconds": 1.0},
        {"item": "0001-1-b-code", "tokens": 20, "seconds": 2.0},
        {"item": "0001-2-c-code", "tokens": 30, "seconds": 3.0},
    ])
    assert cost_rollup(str(path), "0001") == {"item": "0001", "tokens": 60, "seconds": 6.0, "runs": 3}
    assert cost_rollup(str(path), "0001-1") == {"item": "0001-1", "tokens": 30, "seconds": 3.0, "runs": 2}


def test_prefix_is_exact(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(path, [{"item": "00011-x", "tokens": 5, "seconds": 1.0}])
    assert cost_rollup(str(path), "0001") == {"item": "0001", "tokens": 0, "seconds": 0.0, "runs": 0}


def test_missing_fields_zero(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(path, [{"item": "0001-1-a-code"}])
    assert cost_rollup(str(path), "0001") == {"item": "0001", "tokens": 0, "seconds": 0.0, "runs": 1}


def test_negative_one_is_zero(tmp_path):
    path = tmp_path / "log.jsonl"
    _write(path, [{"item": "0001-1-a-code", "tokens": -1, "seconds": 1.0}])
    assert cost_rollup(str(path), "0001") == {"item": "0001", "tokens": 0, "seconds": 1.0, "runs": 1}


def test_missing_file_zeros(tmp_path):
    path = tmp_path / "does_not_exist.jsonl"
    assert cost_rollup(str(path), "0001") == {"item": "0001", "tokens": 0, "seconds": 0.0, "runs": 0}
