import os
import pathlib

from prove_once.prove_once import prove_once
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item

_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _config(tmp_path):
    text = (_ROOT / "roles" / "board.toml").read_text()
    text = text.replace("wip = 8", "wip = 9", 1)
    dest = tmp_path / "board.toml"
    dest.write_text(text)
    return str(dest)


def _create(title, labels, parent=None):
    args = ["create", title, "-t", "task", "--no-inherit-labels", "-l", labels]
    if parent:
        args += ["--parent", parent]
    return record_run(args)["id"]


def test_empty_prove_noop(bd_repo, tmp_path):
    config_path = _config(tmp_path)

    result = prove_once(config_path)

    assert result == []
    assert record_run(["list", "--all", "--type", "event"]) == []


def test_processes_checking_job(bd_repo, tmp_path):
    config_path = _config(tmp_path)
    item_id = _create("widget code", "kind:code,state:checking")
    record_run(["comment", item_id, 'usage: {"tokens": 5, "seconds": 1.0}'])

    folder = pathlib.Path("src") / "widget"
    folder.mkdir(parents=True)
    (folder / "widget.py").write_text("def widget(x: int) -> int:\n    return x + 1\n")
    (folder / "widget.md").write_text(
        f"widget note line 1\nJob id: {item_id}\nline 3\nline 4\nline 5\nline 6\n"
    )
    os.system("git add -A")
    os.system("git commit -q -m widget")

    result = prove_once(config_path)

    assert result == [item_id]
    assert record_show_item(item_id)["state"] == "done"


def test_story_moves_to_checking(bd_repo, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    code_id = _create("Story S code", "kind:code,state:done", parent=story_id)
    _create("Story S test", "kind:test,state:done", parent=code_id)

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "checking"


def test_story_stays_when_test_open(bd_repo, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    code_id = _create("Story S code", "kind:code,state:done", parent=story_id)
    _create("Story S test", "kind:test,state:ready", parent=code_id)

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "ready"
