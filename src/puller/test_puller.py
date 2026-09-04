from pathlib import Path

import pytest

from puller.puller import puller


def _write_config(path: Path, poll_seconds: int) -> None:
    path.write_text(
        "\n".join(
            [
                "[columns.build]",
                'kinds = ["code"]',
                'states = ["ready"]',
                'role = "builder"',
                'tier = "cheap"',
                "wip = 4",
                f"poll_seconds = {poll_seconds}",
                "",
                "[limits]",
                "max_parallel_model_runs = 1",
                "claim_timeout_seconds = 60",
                "",
            ]
        )
    )


def _write_human_config(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "[columns.intent_new]",
                'kinds = ["intent"]',
                'states = ["waiting"]',
                'role = "board"',
                'tier = "human"',
                "wip = 2",
                "poll_seconds = 0",
                "",
                "[limits]",
                "max_parallel_model_runs = 1",
                "claim_timeout_seconds = 60",
                "",
            ]
        )
    )


def test_stops_on_file(tmp_path):
    config_path = tmp_path / "board.toml"
    _write_config(config_path, 30)
    stop_file = tmp_path / "stop"
    stop_file.touch()

    def once(role, config_path, invoke):
        raise AssertionError("once should not be called")

    result = puller(
        "builder",
        str(config_path),
        None,
        {"stop_file": str(stop_file), "once": once},
    )

    assert result == 0


def test_passes_counted(tmp_path):
    config_path = tmp_path / "board.toml"
    _write_config(config_path, 1)
    stop_file = tmp_path / "stop"
    calls = {"count": 0}

    def once(role, config_path, invoke):
        calls["count"] += 1
        if calls["count"] == 2:
            Path(stop_file).touch()

    result = puller(
        "builder",
        str(config_path),
        None,
        {"stop_file": str(stop_file), "once": once},
    )

    assert result == 2


def test_human_role_raises(tmp_path):
    config_path = tmp_path / "board.toml"
    _write_human_config(config_path)
    stop_file = tmp_path / "stop"

    def once(role, config_path, invoke):
        raise AssertionError("once should not be called")

    with pytest.raises(ValueError):
        puller(
            "board",
            str(config_path),
            None,
            {"stop_file": str(stop_file), "once": once},
        )
