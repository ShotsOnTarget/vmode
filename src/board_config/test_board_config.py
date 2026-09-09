import pytest

from board_config.board_config import board_config


def test_shipped_config_loads():
    config = board_config("roles/board.toml")
    assert set(config["columns"]) == {
        "intent_new",
        "story_todo",
        "sheet_todo",
        "building",
        "build",
        "test",
        "prove",
        "verify",
        "validate",
        "triage",
        "learn",
        "blocked",
        "architect_notes",
        "engineer_notes",
    }


def test_shipped_sheet_todo_is_the_engineers():
    config = board_config("roles/board.toml")
    column = config["columns"]["sheet_todo"]
    assert column["role"] == "engineer"
    assert column["tier"] == "engineer"
    assert column["adapter"]
    assert column["labels_absent"] == ["cut"]


def test_shipped_building_column_is_stories_ready():
    config = board_config("roles/board.toml")
    column = config["columns"]["building"]
    assert column["kinds"] == ["story"]
    assert column["states"] == ["ready"]
    assert column["role"] == "none"


def test_conflict_raises(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.a]
kinds = ["code"]
states = ["ready"]
role = "builder"
tier = "cheap"
wip = 1
poll_seconds = 30

[columns.b]
kinds = ["code"]
states = ["ready"]
role = "builder"
tier = "cheap"
wip = 1
poll_seconds = 30

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    with pytest.raises(ValueError):
        board_config(str(toml_path))


def test_bad_tier_raises(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.a]
kinds = ["code"]
states = ["ready"]
role = "builder"
tier = "gpt"
wip = 1
poll_seconds = 30

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    with pytest.raises(ValueError):
        board_config(str(toml_path))


def test_unknown_key_raises(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.a]
kinds = ["code"]
states = ["ready"]
role = "builder"
tier = "cheap"
wip = 1
poll_seconds = 30
colour = "blue"

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    with pytest.raises(ValueError):
        board_config(str(toml_path))


def test_missing_file_raises(tmp_path):
    missing_path = tmp_path / "does_not_exist.toml"
    with pytest.raises(FileNotFoundError):
        board_config(str(missing_path))


def test_disjoint_owner_columns_load(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.a]
kinds = ["note"]
states = ["waiting", "ready"]
role = "none"
tier = "none"
wip = 1
poll_seconds = 0
owners = ["architect"]

[columns.b]
kinds = ["note"]
states = ["waiting", "ready"]
role = "none"
tier = "none"
wip = 1
poll_seconds = 0
owners = ["engineer"]

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    config = board_config(str(toml_path))
    assert config["columns"]["a"]["owners"] == ["architect"]
    assert config["columns"]["b"]["owners"] == ["engineer"]


def test_overlapping_owner_columns_raise(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.a]
kinds = ["note"]
states = ["waiting", "ready"]
role = "none"
tier = "none"
wip = 1
poll_seconds = 0
owners = ["architect"]

[columns.b]
kinds = ["note"]
states = ["waiting", "ready"]
role = "none"
tier = "none"
wip = 1
poll_seconds = 0
owners = ["architect"]

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    with pytest.raises(ValueError):
        board_config(str(toml_path))


def test_ownerless_and_owner_column_raise(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.a]
kinds = ["note"]
states = ["waiting", "ready"]
role = "none"
tier = "none"
wip = 1
poll_seconds = 0

[columns.b]
kinds = ["note"]
states = ["waiting", "ready"]
role = "none"
tier = "none"
wip = 1
poll_seconds = 0
owners = ["engineer"]

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    with pytest.raises(ValueError):
        board_config(str(toml_path))


def test_shipped_note_columns_and_triage_owners():
    config = board_config("roles/board.toml")
    for name in ("architect_notes", "engineer_notes"):
        column = config["columns"][name]
        assert column["role"] == "none"
        assert column["tier"] == "none"
        assert column["poll_seconds"] == 0
    assert config["columns"]["triage"]["owners"] == ["analyst", "supervisor"]
