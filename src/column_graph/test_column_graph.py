import pathlib

import pytest

from board_config.board_config import board_config
from column_graph.column_graph import column_graph
from record_add_link.record_add_link import record_add_link
from record_run.record_run import record_run

_BOARD = str(pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml")


def _make(kind, state):
    created = record_run(
        ["create", "-l", f"kind:{kind},state:{state}", "--no-inherit-labels", "Item"]
    )
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def test_only_the_columns_own_kinds_and_states_are_fetched(fake_bd):
    wanted = _make("code", "ready")
    _make("code", "done")
    _make("story", "ready")

    graph, labels = column_graph("build", board_config(_BOARD))

    assert list(graph) == [wanted]
    assert labels[wanted] == ["kind:code", "state:ready"]


def test_in_progress_is_fetched_so_the_wip_count_is_right(fake_bd):
    busy = _make("code", "in_progress")

    graph, _ = column_graph("build", board_config(_BOARD))

    assert graph[busy]["state"] == "in_progress"


def test_an_item_the_column_needs_first_is_fetched_too(fake_bd):
    first = _make("test", "done")
    waits = _make("code", "ready")
    record_add_link("needs_first", waits, first)

    graph, _ = column_graph("build", board_config(_BOARD))

    assert graph[waits]["needs"] == [first]
    assert graph[first]["state"] == "done"


def test_unknown_column_refused(fake_bd):
    with pytest.raises(ValueError):
        column_graph("no-such-column", board_config(_BOARD))
