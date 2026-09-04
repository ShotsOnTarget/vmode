import pathlib

import pytest
from prove_move.prove_move import prove_move

from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _create(state, extra_labels=None):
    labels = [f"kind:code,state:{state}"]
    if extra_labels:
        labels[0] += "," + ",".join(extra_labels)
    return record_run(
        [
            "create",
            "x item",
            "-t",
            "task",
            "--no-inherit-labels",
            "-l",
            labels[0],
        ]
    )["id"]


def _labels(item_id):
    names = []
    for label in record_run(["label", "list", item_id]):
        names.append(label if isinstance(label, str) else label.get("name", ""))
    return names


def test_bounce_sets_label_and_note(bd_repo):
    item_id = _create("checking")
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 1,
        "rules": ["lint_findings"],
    }

    prove_move(item_id, outcome)

    shown = record_show_item(item_id)
    assert shown["state"] == "ready"
    assert "retry:1" in _labels(item_id)
    row = record_run(["show", item_id])
    row = row[0] if isinstance(row, list) else row
    comments = row.get("comments", [])
    assert row.get("comment_count", len(comments)) >= 1


def test_bounce_replaces_retry_label(bd_repo):
    item_id = _create("checking", extra_labels=["retry:1"])
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 2,
        "rules": ["lint_findings"],
    }

    prove_move(item_id, outcome)

    labels = _labels(item_id)
    assert "retry:2" in labels
    assert "retry:1" not in labels


def test_escalate_writes_summary(bd_repo):
    item_id = _create("checking")
    outcome = {
        "action": "escalate",
        "state": "blocked",
        "retries": 3,
        "rules": ["over_50_lines"],
    }
    summary_path = pathlib.Path("work/summaries") / f"{item_id}.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        prove_move(item_id, outcome)

        shown = record_show_item(item_id)
        assert shown["state"] == "blocked"
        assert summary_path.is_file()
        assert "over_50_lines" in summary_path.read_text()
    finally:
        if summary_path.is_file():
            summary_path.unlink()


def test_done_sets_state(bd_repo):
    item_id = _create("checking")
    outcome = {
        "action": "log_done",
        "state": "done",
        "retries": 0,
        "rules": [],
    }

    prove_move(item_id, outcome)

    shown = record_show_item(item_id)
    assert shown["state"] == "done"


def test_missing_key_raises(bd_repo):
    item_id = _create("checking")
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 1,
    }

    with pytest.raises(ValueError):
        prove_move(item_id, outcome)
