import pytest

from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

_STATES = (
    "waiting",
    "ready",
    "in_progress",
    "blocked",
    "checking",
    "done",
    "reopened",
)


def _make_item():
    item = record_run(
        ["create", "-l", "kind:task", "-t", "task", "-a", "alice", "Item"]
    )
    return item["id"]


def _show(item_id):
    return record_run(["show", item_id])[0]


def _state_labels(item_id):
    labels = _show(item_id)["labels"]
    return [label for label in labels if label.startswith("state:")]


def test_each_state_sets(fake_bd):
    item_id = _make_item()
    for state in _STATES:
        record_set_state(item_id, state)
        state_labels = _state_labels(item_id)
        assert state_labels == [f"state:{state}"]


def test_eighth_state_rejected(fake_bd):
    item_id = _make_item()
    with pytest.raises(ValueError):
        record_set_state(item_id, "paused")


def test_done_closes(fake_bd):
    item_id = _make_item()
    record_set_state(item_id, "done")
    assert _show(item_id)["status"] == "closed"


def test_reopened_opens(fake_bd):
    item_id = _make_item()
    record_set_state(item_id, "done")
    record_set_state(item_id, "reopened")
    assert _show(item_id)["status"] == "open"


def test_state_change_is_one_write(fake_bd, monkeypatch):
    """Label off, label on and status set travel in one update, so a failed
    write leaves the old state, never none (2026-09-09)."""
    import record_set_state.record_set_state as mod

    item_id = _make_item()
    record_set_state(item_id, "waiting")
    calls = []
    real = mod.record_run

    def spy(args):
        calls.append(list(args))
        return real(args)

    monkeypatch.setattr(mod, "record_run", spy)
    record_set_state(item_id, "ready")
    writes = [c for c in calls if c[0] == "update"]
    assert len(writes) == 1
    assert "--remove-label" in writes[0] and "--add-label" in writes[0]
    assert _state_labels(item_id) == ["state:ready"]


def test_reopened_clears_claim(fake_bd):
    """A reopened job is anyone's to take, not its last builder's."""
    item_id = _make_item()
    record_run(["update", item_id, "-a", "builder-7"])
    record_set_state(item_id, "done")
    assert _show(item_id)["assignee"] == "builder-7"
    record_set_state(item_id, "reopened")
    assert not _show(item_id)["assignee"]


def test_ready_needs_checklist(fake_bd):
    story = record_run(["create", "S", "-t", "task", "-l", "kind:story,state:waiting"])
    with pytest.raises(ValueError):
        record_set_state(story["id"], "ready")
    record_run(["update", story["id"], "--acceptance", "1. it works [testing]"])
    assert record_set_state(story["id"], "ready")["state"] == "ready"
