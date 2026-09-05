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


def _note_children(job_id):
    row = record_run(["show", job_id])
    row = row[0] if isinstance(row, list) else row
    notes = []
    for dep in row.get("dependents", []):
        if dep.get("dependency_type") != "parent-child":
            continue
        if "kind:note" in dep.get("labels", []):
            notes.append(dep["id"])
    return notes


def test_bounce_raises_note(fake_bd):
    item_id = _create("checking")
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 1,
        "rules": ["lint_findings"],
    }

    prove_move(item_id, outcome)

    notes = _note_children(item_id)
    assert len(notes) == 1
    assert record_show_item(notes[0])["parent"] == item_id


def test_escalate_raises_note_no_file(fake_bd):
    item_id = _create("checking")
    outcome = {
        "action": "escalate",
        "state": "blocked",
        "retries": 3,
        "rules": ["over_50_lines"],
    }
    summary_path = pathlib.Path("work/summaries") / f"{item_id}.md"

    prove_move(item_id, outcome)

    assert len(_note_children(item_id)) == 1
    assert not summary_path.is_file()


def test_bounce_clears_claim(fake_bd):
    item_id = _create("checking")
    record_run(["update", item_id, "--claim", "--actor", "builder-x"])
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 1,
        "rules": ["lint_findings"],
    }

    prove_move(item_id, outcome)

    row = record_run(["show", item_id])
    row = row[0] if isinstance(row, list) else row
    assert not row.get("assignee")


def test_retry_label_set(fake_bd):
    item_id = _create("checking")
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 2,
        "rules": ["lint_findings"],
    }

    prove_move(item_id, outcome)

    retry_labels = [label for label in _labels(item_id) if label.startswith("retry:")]
    assert retry_labels == ["retry:2"]


def test_bounce_sets_label_and_note(fake_bd):
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


def test_bounce_replaces_retry_label(fake_bd):
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


def test_done_sets_state(fake_bd):
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


def test_missing_key_raises(fake_bd):
    item_id = _create("checking")
    outcome = {
        "action": "bounce",
        "state": "ready",
        "retries": 1,
    }

    with pytest.raises(ValueError):
        prove_move(item_id, outcome)
