import pytest

from board_config.board_config import board_config
from column_items.column_items import column_items


def test_lists_matching():
    config = board_config("roles/board.toml")
    graph = {
        "c1": {"id": "c1", "kind": "code", "state": "ready", "needs": []},
        "c2": {"id": "c2", "kind": "code", "state": "ready", "needs": []},
        "t1": {"id": "t1", "kind": "test", "state": "ready", "needs": []},
    }
    labels = {"c1": [], "c2": [], "t1": []}

    result = column_items("build", graph, labels, config)

    assert [item["id"] for item in result] == ["c1", "c2"]


def test_excludes_blocked_by_needs():
    config = board_config("roles/board.toml")
    graph = {
        "x": {"id": "x", "kind": "code", "state": "waiting"},
        "c1": {"id": "c1", "kind": "code", "state": "ready", "needs": ["x"]},
    }
    labels = {"x": [], "c1": []}

    result = column_items("build", graph, labels, config)

    assert result == []


def test_includes_when_needs_done():
    config = board_config("roles/board.toml")
    graph = {
        "x": {"id": "x", "kind": "code", "state": "done"},
        "c1": {"id": "c1", "kind": "code", "state": "ready", "needs": ["x"]},
    }
    labels = {"x": [], "c1": []}

    result = column_items("build", graph, labels, config)

    assert [item["id"] for item in result] == ["c1"]


def test_unknown_column_raises():
    config = board_config("roles/board.toml")

    with pytest.raises(ValueError):
        column_items("not_a_column", {}, {}, config)
