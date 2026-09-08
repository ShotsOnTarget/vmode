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


def test_gating_column_ignores_needs():
    config = board_config("roles/board.toml")
    graph = {
        "x": {"id": "x", "kind": "code", "state": "waiting"},
        "c1": {"id": "c1", "kind": "code", "state": "checking", "needs": ["x"]},
    }
    labels = {"x": [], "c1": []}

    result = column_items("prove", graph, labels, config)

    assert [item["id"] for item in result] == ["c1"]


def _story_and_job(story_state, job_state="ready"):
    return {
        "s": {"id": "s", "kind": "story", "state": story_state, "needs": []},
        "c1": {
            "id": "c1",
            "kind": "code",
            "state": job_state,
            "needs": [],
            "parent": "s",
        },
    }


def test_a_job_under_a_blocked_story_is_not_offered():
    config = board_config("roles/board.toml")
    graph = _story_and_job("blocked")

    assert column_items("build", graph, {"s": [], "c1": []}, config) == []


def test_a_job_under_a_story_still_being_cut_is_not_offered():
    config = board_config("roles/board.toml")
    graph = _story_and_job("in_progress")

    assert column_items("build", graph, {"s": [], "c1": []}, config) == []


def test_a_job_under_a_released_story_is_offered():
    config = board_config("roles/board.toml")
    for state in ("ready", "checking", "done"):
        graph = _story_and_job(state)
        result = column_items("build", graph, {"s": [], "c1": []}, config)
        assert [item["id"] for item in result] == ["c1"], state


def test_a_job_whose_story_is_not_in_the_graph_is_still_offered():
    config = board_config("roles/board.toml")
    graph = {
        "c1": {"id": "c1", "kind": "code", "state": "ready", "needs": [], "parent": "s"}
    }

    result = column_items("build", graph, {"c1": []}, config)

    assert [item["id"] for item in result] == ["c1"]


def test_gating_column_ignores_the_story():
    config = board_config("roles/board.toml")
    graph = _story_and_job("blocked", "checking")

    result = column_items("prove", graph, {"s": [], "c1": []}, config)

    assert [item["id"] for item in result] == ["c1"]
