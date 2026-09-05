import json

import pytest

from log_migrate.log_migrate import log_migrate
from log_read_item.log_read_item import log_read_item
from record_run.record_run import record_run

NL = chr(10)


def _item():
    labels = "kind:code,state:done"
    args = ["create", "J", "-t", "task", "-l", labels, "--no-inherit-labels"]
    return record_run(args)["id"]


def _line(item_id, **extra):
    base = {
        "ts": "2026-09-01T00:00:00+00:00",
        "item": item_id,
        "gate": "Built",
        "rule": "pass",
        "inputs": {},
        "state": "done",
    }
    return json.dumps({**base, **extra})


def test_migrates_lines(fake_bd, tmp_path):
    item_id = _item()
    path = tmp_path / "log.jsonl"
    path.write_text(_line(item_id, tokens=5, seconds=1.0) + NL + _line(item_id) + NL)
    assert log_migrate(str(path)) == 2
    events = log_read_item(item_id)
    assert len(events) == 2
    assert all("ts_original" in e["inputs"] for e in events)


def test_defaults_applied(fake_bd, tmp_path):
    item_id = _item()
    path = tmp_path / "log.jsonl"
    path.write_text(_line(item_id) + NL)
    log_migrate(str(path))
    assert log_read_item(item_id)[0]["tokens"] == -1


def test_bad_line_raises(fake_bd, tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text("not json at all" + NL)
    with pytest.raises(ValueError):
        log_migrate(str(path))
