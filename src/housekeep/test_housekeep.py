import pytest

from housekeep.housekeep import housekeep
from log_read_item.log_read_item import log_read_item
from record_run.record_run import record_run


def _claimed_item(title: str, claim: str) -> str:
    created = record_run(
        [
            "create",
            title,
            "-t",
            "task",
            "-l",
            "kind:code,state:in_progress",
            "-a",
            claim,
        ]
    )
    return created["id"]


class _Usage:
    def __init__(self, free):
        self.free = free


def test_low_disk_is_logged_on_an_open_intent(fake_bd, monkeypatch):
    """Under two gigabytes free, one Housekeep low_disk event names the free
    space; with room, none (the drive filled unseen on 2026-09-09)."""
    intent = record_run(
        ["create", "I", "-t", "epic", "-l", "kind:intent,state:in_progress"]
    )["id"]
    usage = "low_disk.low_disk.shutil.disk_usage"
    monkeypatch.setattr(usage, lambda p: _Usage(2**30))
    result = housekeep(".")
    assert result["low_disk"] == 1.0
    events = log_read_item(intent)
    assert len(events) == 1 and events[0]["rule"] == "low_disk"
    assert "1.0 GB free" in str(events[0]["inputs"])
    monkeypatch.setattr(usage, lambda p: _Usage(9 * 2**30))
    assert housekeep(".")["low_disk"] is None
    assert len(log_read_item(intent)) == 1


def test_housekeep_writes_one_log_entry_per_released_claim(fake_bd):
    first = _claimed_item("w code", "builder-99999999")
    second = _claimed_item("v code", "builder-99999997")

    result = housekeep(".")

    assert first in result["released"]
    assert second in result["released"]
    assert len(log_read_item(first)) == 1
    assert len(log_read_item(second)) == 1


def test_housekeep_log_entry_names_item_and_claim(fake_bd):
    claim = "builder-99999998"
    item = _claimed_item("w code", claim)

    result = housekeep(".")

    assert item in result["released"]
    events = log_read_item(item)
    assert len(events) == 1
    assert events[0]["item"] == item
    assert events[0]["inputs"] == claim


def test_a_stale_unchecked_note_is_cleared(fake_bd):
    intent = record_run(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,state:ready,owner:board",
            "--no-inherit-labels",
        ]
    )["id"]
    note = record_run(
        [
            "create",
            f"unchecked: {intent}",
            "-t",
            "task",
            "-l",
            "kind:note,state:waiting,owner:supervisor",
            "--no-inherit-labels",
            "--parent",
            intent,
        ]
    )["id"]
    validation = record_run(
        [
            "create",
            "V",
            "-t",
            "task",
            "-l",
            "kind:validation,state:waiting,owner:board",
            "--no-inherit-labels",
        ]
    )["id"]
    record_run(["dep", "add", validation, intent, "-t", "validates"])

    result = housekeep(".")

    assert note in result["cleared"]
    assert "state:done" in record_run(["show", note])[0]["labels"]


def _stale_unchecked_note(owner: str) -> tuple[str, str]:
    intent = record_run(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,state:ready,owner:board",
            "--no-inherit-labels",
        ]
    )["id"]
    note = record_run(
        [
            "create",
            f"unchecked: {intent}",
            "-t",
            "task",
            "-l",
            f"kind:note,state:waiting,owner:{owner}",
            "--no-inherit-labels",
            "--parent",
            intent,
        ]
    )["id"]
    validation = record_run(
        [
            "create",
            "V",
            "-t",
            "task",
            "-l",
            "kind:validation,state:waiting,owner:board",
            "--no-inherit-labels",
        ]
    )["id"]
    record_run(["dep", "add", validation, intent, "-t", "validates"])
    return intent, note


@pytest.mark.parametrize("owner", ["architect", "engineer", "analyst"])
def test_housekeep_does_not_clear_other_role_finding_note(fake_bd, owner):
    _, note = _stale_unchecked_note(owner)

    result = housekeep(".")

    assert note not in result["cleared"]
    assert "state:waiting" in record_run(["show", note])[0]["labels"]


def test_housekeep_still_clears_supervisor_finding_note(fake_bd):
    intent = record_run(
        [
            "create",
            "I",
            "-t",
            "epic",
            "-l",
            "kind:intent,state:ready,owner:board",
            "--no-inherit-labels",
        ]
    )["id"]
    validation = record_run(
        [
            "create",
            "V",
            "-t",
            "task",
            "-l",
            "kind:validation,state:waiting,owner:board",
            "--no-inherit-labels",
        ]
    )["id"]
    note = record_run(
        [
            "create",
            f"checks_nothing: {validation}",
            "-t",
            "task",
            "-l",
            "kind:note,state:waiting,owner:supervisor",
            "--no-inherit-labels",
            "--parent",
            validation,
        ]
    )["id"]
    record_run(["dep", "add", validation, intent, "-t", "validates"])

    result = housekeep(".")

    assert note in result["cleared"]
    assert "state:done" in record_run(["show", note])[0]["labels"]
