import pathlib
import re

from pull_once.pull_once import pull_once
from record_run.record_run import record_run

_BOARD_TOML = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _make_item():
    created = record_run(
        ["create", "-l", "kind:code,state:ready", "--no-inherit-labels", "Item"]
    )
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _make_kind(kind, state):
    created = record_run(
        ["create", "-l", f"kind:{kind},state:{state}", "--no-inherit-labels", "Item"]
    )
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _cap_config(tmp_path, cap, name="board.toml"):
    text = _BOARD_TOML.read_text()
    text = re.sub(
        r"max_parallel_model_runs = \d+", f"max_parallel_model_runs = {cap}", text
    )
    dest = tmp_path / name
    dest.write_text(text)
    return str(dest)


def _ghost_config(tmp_path, cap, name="board.toml"):
    text = _BOARD_TOML.read_text()
    text = re.sub(
        r"max_parallel_model_runs = \d+", f"max_parallel_model_runs = {cap}", text
    )
    text += (
        "\n[columns.ghost]\n"
        'kinds = ["pattern"]\n'
        'states = ["ready"]\n'
        'role = "none"\n'
        'tier = "frontier"\n'
        "wip = 1\n"
        "poll_seconds = 0\n"
    )
    dest = tmp_path / name
    dest.write_text(text)
    return str(dest)


def _ok_invoke(item, column):
    return {"tokens": 3, "seconds": 0.5, "report": "ok"}


def test_global_headroom_ignores_intent(fake_bd, tmp_path):
    _make_kind("intent", "in_progress")
    ready_id = _make_item()
    config_path = _cap_config(tmp_path, 1, name="cap1.toml")

    assert pull_once("builder", config_path, _ok_invoke) == [ready_id]


def test_global_headroom_returns_full_cap_with_only_intents(fake_bd, tmp_path):
    _make_kind("intent", "in_progress")
    _make_kind("intent", "in_progress")
    first = _make_item()
    second = _make_item()
    config_path = _cap_config(tmp_path, 2, name="cap2.toml")

    assert pull_once("builder", config_path, _ok_invoke) == [first, second]


def test_global_headroom_uses_pulled_columns(fake_bd, tmp_path):
    _make_kind("pattern", "in_progress")
    first = _make_item()
    config_path = _ghost_config(tmp_path, 1, name="ghost.toml")

    assert pull_once("builder", config_path, _ok_invoke) == [first]

    _make_kind("code", "in_progress")
    _make_item()

    assert pull_once("builder", config_path, _ok_invoke) == []


def test_global_headroom_counts_modelled_work(fake_bd, tmp_path):
    _make_kind("code", "in_progress")
    _make_kind("test", "in_progress")
    _make_kind("note", "in_progress")
    _make_kind("proposal", "in_progress")
    _make_item()
    config_path = _cap_config(tmp_path, 4, name="cap4.toml")

    assert pull_once("builder", config_path, _ok_invoke) == []
