import pathlib

from board_config.board_config import board_config
from columns_rows.columns_rows import columns_rows
from record_run.record_run import record_run

_BOARD = str(pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml")


def _make(kind, state, extra=""):
    labels = f"kind:{kind},state:{state}" + (f",{extra}" if extra else "")
    created = record_run(["create", "-l", labels, "--no-inherit-labels", "Item"])
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _ids(rows):
    return sorted(row["id"] for row in rows)


def test_live_states_are_fetched_and_done_jobs_are_not(fake_bd):
    ready = _make("code", "ready")
    busy = _make("test", "in_progress")
    blocked = _make("story", "blocked")
    _make("code", "done")
    _make("test", "done")

    rows = columns_rows(board_config(_BOARD))

    assert _ids(rows) == sorted([ready, busy, blocked])


def test_done_stories_are_fetched_for_the_learn_column(fake_bd):
    story = _make("story", "done")
    learned = _make("story", "done", "learned")

    rows = columns_rows(board_config(_BOARD))

    assert _ids(rows) == sorted([story, learned])


def test_events_are_excluded(fake_bd):
    kept = _make("code", "ready")
    created = record_run(["create", "-t", "event", "-l", "kind:code,state:ready", "Ev"])
    item = created[0] if isinstance(created, list) else created
    assert item["id"] != kept

    rows = columns_rows(board_config(_BOARD))

    assert _ids(rows) == [kept]
