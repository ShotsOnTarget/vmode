import pytest

from board_config.board_config import board_config
from column_of.column_of import column_of


def test_story_waiting_is_sheet_todo():
    config = board_config("roles/board.toml")
    item = {"kind": "story", "state": "waiting"}
    assert column_of(item, [], config) == "sheet_todo"


def test_test_ready_is_test():
    config = board_config("roles/board.toml")
    item = {"kind": "test", "state": "ready"}
    assert column_of(item, [], config) == "test"


def test_learned_story_is_none():
    config = board_config("roles/board.toml")
    item = {"kind": "story", "state": "done"}
    assert column_of(item, ["learned"], config) is None
    assert column_of(item, [], config) == "learn"


def test_two_matches_raise():
    config = {
        "columns": {
            "a": {"kinds": ["story"], "states": ["waiting"]},
            "b": {"kinds": ["story"], "states": ["waiting"]},
        }
    }
    item = {"kind": "story", "state": "waiting"}
    with pytest.raises(ValueError):
        column_of(item, [], config)
