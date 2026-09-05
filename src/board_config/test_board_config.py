import pytest

from board_config.board_config import board_config


def test_shipped_config_loads():
    config = board_config("roles/board.toml")
    assert isinstance(config, dict)
    assert len(config["columns"]) == 12


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
