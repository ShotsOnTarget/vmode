from log_read_item.log_read_item import log_read_item
from low_disk.low_disk import low_disk
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


class _Usage:
    def __init__(self, free):
        self.free = free


def _intent(state="in_progress"):
    args = ["create", "I", "-t", "epic", "-l", f"kind:intent,state:{state}"]
    return record_run(args)["id"]


def test_short_drive_logs_one_event_on_an_open_intent(fake_bd, monkeypatch):
    intent = _intent()
    monkeypatch.setattr("low_disk.low_disk.shutil.disk_usage", lambda p: _Usage(2**30))
    assert low_disk(".", record_graph()) == 1.0
    events = log_read_item(intent)
    assert len(events) == 1
    assert events[0]["rule"] == "low_disk"
    assert "1.0 GB free" in str(events[0]["inputs"])


def test_room_logs_nothing(fake_bd, monkeypatch):
    intent = _intent()
    monkeypatch.setattr(
        "low_disk.low_disk.shutil.disk_usage", lambda p: _Usage(9 * 2**30)
    )
    assert low_disk(".", record_graph()) is None
    assert log_read_item(intent) == []


def test_short_drive_with_only_done_intents_returns_the_figure(fake_bd, monkeypatch):
    intent = _intent("done")
    monkeypatch.setattr("low_disk.low_disk.shutil.disk_usage", lambda p: _Usage(2**29))
    assert low_disk(".", record_graph()) == 0.5
    assert log_read_item(intent) == []
