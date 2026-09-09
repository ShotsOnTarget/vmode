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


def test_owner_rule_matches_only_listed_owner():
    config = {
        "columns": {
            "architect_notes": {
                "kinds": ["note"],
                "states": ["waiting"],
                "owners": ["architect"],
            }
        }
    }
    listed = {"kind": "note", "state": "waiting", "owner": "architect"}
    other = {"kind": "note", "state": "waiting", "owner": "engineer"}
    assert column_of(listed, [], config) == "architect_notes"
    assert column_of(other, [], config) is None


def test_rule_without_owners_matches_any_owner():
    config = {
        "columns": {
            "build": {
                "kinds": ["code"],
                "states": ["ready"],
            }
        }
    }
    item = {"kind": "code", "state": "ready", "owner": "architect"}
    assert column_of(item, [], config) == "build"
    item["owner"] = "engineer"
    assert column_of(item, [], config) == "build"
    item["owner"] = "supervisor"
    assert column_of(item, [], config) == "build"


def test_shipped_note_columns_partition_notes_by_owner():
    config = {
        "columns": {
            "architect_notes": {
                "kinds": ["note"],
                "states": ["waiting", "ready", "in_progress"],
                "owners": ["architect"],
            },
            "engineer_notes": {
                "kinds": ["note"],
                "states": ["waiting", "ready", "in_progress"],
                "owners": ["engineer"],
            },
            "triage": {
                "kinds": ["note"],
                "states": ["waiting", "ready", "in_progress"],
                "owners": ["analyst", "supervisor"],
            },
        }
    }
    architect = {"kind": "note", "state": "ready", "owner": "architect"}
    engineer = {"kind": "note", "state": "ready", "owner": "engineer"}
    analyst = {"kind": "note", "state": "ready", "owner": "analyst"}
    supervisor = {"kind": "note", "state": "ready", "owner": "supervisor"}
    assert column_of(architect, [], config) == "architect_notes"
    assert column_of(engineer, [], config) == "engineer_notes"
    assert column_of(analyst, [], config) == "triage"
    assert column_of(supervisor, [], config) == "triage"
