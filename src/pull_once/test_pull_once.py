import pathlib
import shutil

import pytest

from pull_once.pull_once import pull_once
from record_run.record_run import record_run

_BOARD_TOML = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _make_item():
    created = record_run(
        ["create", "-l", "kind:code,state:ready", "--no-inherit-labels", "Item"]
    )
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _make_in_progress_item():
    created = record_run(
        [
            "create",
            "-l",
            "kind:code,state:in_progress",
            "--no-inherit-labels",
            "Item",
        ]
    )
    item = created[0] if isinstance(created, list) else created
    record_run(["update", item["id"], "--claim", "--actor", "someone-else"])
    return item["id"]


def _make_done_story():
    created = record_run(
        ["create", "-l", "kind:story,state:done", "--no-inherit-labels", "Item"]
    )
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _show(item_id):
    shown = record_run(["show", item_id])
    return shown[0] if isinstance(shown, list) else shown


def _last_comment_text(item_id):
    row = _show(item_id)
    comments = row.get("comments", [])
    return comments[-1]["text"] if comments else ""


def _set_build_wip(text: str, value: int) -> str:
    lines = text.splitlines()
    out = []
    in_build = False
    for line in lines:
        if line.startswith("[columns."):
            in_build = line.split("#")[0].strip() == "[columns.build]"
        if in_build and line.strip().startswith("wip"):
            line = f"wip = {value}"
        out.append(line)
    return "\n".join(out) + "\n"


def _plain_config(tmp_path):
    dest = tmp_path / "board.toml"
    shutil.copy(_BOARD_TOML, dest)
    return str(dest)


def _config_with_build_wip(tmp_path, value, name="board.toml"):
    dest = tmp_path / name
    text = _BOARD_TOML.read_text()
    dest.write_text(_set_build_wip(text, value))
    return str(dest)


def _ok_invoke(item, column):
    return {"tokens": 3, "seconds": 0.5, "report": "ok"}


def _raising_invoke(item, column):
    raise RuntimeError("boom")


def test_claims_within_wip(fake_bd, tmp_path):
    _make_in_progress_item()
    ready_id = _make_item()

    config_wip_1 = _config_with_build_wip(tmp_path, 1, name="wip1.toml")
    claimed_at_1 = pull_once("builder", config_wip_1, _ok_invoke)
    assert claimed_at_1 == []

    config_wip_2 = _config_with_build_wip(tmp_path, 2, name="wip2.toml")
    claimed_at_2 = pull_once("builder", config_wip_2, _ok_invoke)
    assert claimed_at_2 == [ready_id]


def test_invoke_result_recorded(fake_bd, tmp_path):
    item_id = _make_item()
    config_path = _plain_config(tmp_path)

    claimed = pull_once("builder", config_path, _ok_invoke)

    assert claimed == [item_id]
    row = _show(item_id)
    assert "state:checking" in row["labels"]
    assert _last_comment_text(item_id).startswith("usage:")


def test_invoke_failure_releases(fake_bd, tmp_path):
    item_id = _make_item()
    config_path = _plain_config(tmp_path)

    claimed = pull_once("builder", config_path, _raising_invoke)

    assert claimed == [item_id]
    row = _show(item_id)
    assert "state:ready" in row["labels"]
    assert not row.get("assignee")
    assert _last_comment_text(item_id).startswith("release:")

    reclaimed = pull_once("builder", config_path, _ok_invoke)

    assert reclaimed == [item_id]


def test_config_change_respected(fake_bd, tmp_path):
    first_ready = _make_item()
    config_path = _config_with_build_wip(tmp_path, 1)

    claimed_first = pull_once("builder", config_path, _ok_invoke)
    assert claimed_first == [first_ready]
    row = _show(first_ready)
    assert "state:checking" in row["labels"]

    _make_item()
    text = _BOARD_TOML.read_text()
    pathlib.Path(config_path).write_text(_set_build_wip(text, 0))

    claimed_second = pull_once("builder", config_path, _ok_invoke)

    assert claimed_second == []


def test_unknown_role_raises(fake_bd, tmp_path):
    config_path = _plain_config(tmp_path)

    with pytest.raises(ValueError):
        pull_once("nobody", config_path, _ok_invoke)


def test_label_column_adds_label(fake_bd, tmp_path):
    story_id = _make_done_story()
    config_path = _plain_config(tmp_path)

    claimed = pull_once("analyst", config_path, _ok_invoke)

    assert claimed == [story_id]
    row = _show(story_id)
    assert "learned" in row["labels"]
    assert "state:done" in row["labels"]
    assert not row.get("assignee")


def test_lost_claim_skipped(fake_bd, tmp_path):
    ready_id = _make_item()
    record_run(["update", ready_id, "--claim", "--actor", "other"])
    config_path = _plain_config(tmp_path)

    claimed = pull_once("builder", config_path, _ok_invoke)

    assert claimed == []
    row = _show(ready_id)
    assert row.get("assignee") == "other"


def test_item_carries_its_labels(fake_bd, tmp_path):
    item_id = _make_item()
    config_path = _plain_config(tmp_path)
    seen = {}

    def _capturing_invoke(item, column):
        seen["item"] = {**item, "labels": list(item.get("labels", []))}
        return _ok_invoke(item, column)

    claimed = pull_once("builder", config_path, _capturing_invoke)

    assert claimed == [item_id]
    assert "labels" in seen["item"]
    assert "kind:code" in seen["item"]["labels"]
    assert "state:ready" in seen["item"]["labels"]
