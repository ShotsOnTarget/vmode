import pytest

from raise_note.raise_note import raise_note
from record_create_item.record_create_item import record_create_item
from record_show_item.record_show_item import record_show_item


def _job(owner="supervisor"):
    intent = record_create_item("intent", "intent", owner)
    return record_create_item("code", "job", owner, parent=intent["id"])["id"]


def test_bounce_note(fake_bd):
    job_id = _job()
    outcome = {"action": "bounce", "retries": 1, "rules": ["tests_failed"]}

    note_id = raise_note(job_id, outcome)

    note = record_show_item(note_id)
    assert note["kind"] == "note"
    assert note["parent"] == job_id
    assert note["title"].startswith("bounce: tests_failed")


def test_escalate_note_has_summary(fake_bd):
    job_id = _job()
    outcome = {"action": "escalate", "retries": 3, "rules": ["tests_failed"]}

    note_id = raise_note(job_id, outcome)

    note = record_show_item(note_id)
    assert "Decision needed" in note["sheet"]
    assert "3" in note["sheet"]


def test_bad_action_rejected(fake_bd):
    job_id = _job()
    outcome = {"action": "log_done", "retries": 0, "rules": []}

    with pytest.raises(ValueError):
        raise_note(job_id, outcome)


def test_bounce_note_owned_by_for_role(fake_bd):
    job_id = _job()
    outcome = {
        "action": "bounce",
        "retries": 1,
        "rules": ["tests_failed"],
        "recipient": "engineer",
    }

    note_id = raise_note(job_id, outcome)

    note = record_show_item(note_id)
    assert note["owner"] == "engineer"
    assert "- **For**: engineer" in note["sheet"]


def test_escalate_note_owned_by_for_role(fake_bd):
    job_id = _job()
    outcome = {
        "action": "escalate",
        "retries": 3,
        "rules": ["tests_failed"],
        "recipient": "architect",
    }

    note_id = raise_note(job_id, outcome)

    note = record_show_item(note_id)
    assert note["owner"] == "architect"
    assert "- **For**: architect" in note["sheet"]


def test_supervisor_finding_note_contract_unchanged(fake_bd):
    job_id = _job()
    outcome = {"action": "bounce", "retries": 1, "rules": ["tests_failed"]}

    note_id = raise_note(job_id, outcome)

    note = record_show_item(note_id)
    assert note["owner"] == "supervisor"
    assert "**For**" not in note["sheet"]
