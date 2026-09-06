import os
import pathlib

from prove_once.prove_once import prove_once
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item

_ROOT = pathlib.Path(__file__).resolve().parents[2]

_CODE_SHEET = """# Instruction sheet
- **Job id**: code-1
- **Kind**: code
- **Function name**: `cutwidget`
- **Folder**: `src/cutwidget/`
- **Signature**: `cutwidget(x: int) -> int`
- **Inputs**: x: a number.
- **Outputs**: Returns the number.
- **Change**: first version.
- **Checklist items this job serves**: 1
"""

_TEST_SHEET = """# Instruction sheet
- **Job id**: test-1
- **Kind**: test
- **Function name**: `cutwidget`
- **Folder**: `src/cutwidget/`
- **Signature**: `cutwidget(x: int) -> int`
- **Inputs**: x: a number.
- **Outputs**: Returns the number.
- **Change**: first version.
- **Checklist items this job serves**: 1
- **Cases**:
  - `test_ok`: works
"""


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


def _create_with_sheet(title, labels, parent, sheet):
    args = [
        "create",
        title,
        "-t",
        "task",
        "--no-inherit-labels",
        "-l",
        labels,
        "--parent",
        parent,
        "-d",
        sheet,
    ]
    return record_run(args)["id"]


def _labels_of(item_id):
    rows = record_run(["label", "list", item_id])
    names = []
    for row in rows:
        if isinstance(row, str):
            names.append(row)
        else:
            names.append(row.get("label") or row.get("name") or "")
    return names


def test_empty_prove_noop(fake_bd, tmp_path):
    config_path = _config(tmp_path)

    result = prove_once(config_path)

    assert result == []
    assert record_run(["list", "--all", "--type", "event"]) == []


def test_processes_checking_job(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    item_id = _create("widget code", "kind:code,state:checking")
    record_run(["comment", item_id, 'usage: {"tokens": 5, "seconds": 1.0}'])

    folder = pathlib.Path("src") / "widget"
    folder.mkdir(parents=True)
    code = (
        "def widget(x: int) -> int:\n    " + '"""Add one."""' + "\n    return x + 1\n"
    )
    (folder / "widget.py").write_text(code)
    (folder / "widget.md").write_text(
        f"widget note line 1\nJob id: {item_id}\nline 3\nline 4\nline 5\nline 6\n"
    )
    os.system("git add -A")
    os.system("git commit -q -m widget")

    result = prove_once(config_path)

    assert result == [item_id]
    assert record_show_item(item_id)["state"] == "done"


def test_story_moves_to_checking(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    code_id = _create("Story S code", "kind:code,state:done", parent=story_id)
    test_id = _create("Story S test", "kind:test,state:done", parent=story_id)
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "checking"


def test_story_stays_when_test_open(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    code_id = _create("Story S code", "kind:code,state:done", parent=story_id)
    test_id = _create("Story S test", "kind:test,state:ready", parent=story_id)
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "ready"


def test_claimed_story_left_alone(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:in_progress")
    record_run(["update", story_id, "-a", "analyst-1"])
    code_id = _create("Story S code", "kind:code,state:done", parent=story_id)
    test_id = _create("Story S test", "kind:test,state:done", parent=story_id)
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "in_progress"


def test_cut_story_gated_to_ready(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    pathlib.Path("src").mkdir(exist_ok=True)
    intent_id = _create("Intent I", "kind:intent,state:waiting")
    story_id = _create("Story S", "kind:story,state:waiting,cut", parent=intent_id)
    record_run(["update", story_id, "--acceptance", "1. works [testing]"])
    code_id = _create_with_sheet(
        "Story S code", "kind:code,state:waiting", story_id, _CODE_SHEET
    )
    test_id = _create_with_sheet(
        "Story S test", "kind:test,state:waiting", story_id, _TEST_SHEET
    )
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])
    verif_id = _create("Verify S", "kind:verification,state:waiting", parent=intent_id)
    record_run(["dep", "add", verif_id, story_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "ready"
    assert record_show_item(code_id)["state"] == "ready"
    assert record_show_item(test_id)["state"] == "ready"


def test_cut_story_with_fault_reopened(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    pathlib.Path("src").mkdir(exist_ok=True)
    intent_id = _create("Intent I", "kind:intent,state:waiting")
    story_id = _create("Story S", "kind:story,state:waiting,cut", parent=intent_id)
    code_id = _create_with_sheet(
        "Story S code", "kind:code,state:waiting", story_id, _CODE_SHEET
    )
    test_id = _create_with_sheet(
        "Story S test", "kind:test,state:waiting", story_id, _TEST_SHEET
    )
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])
    verif_id = _create("Verify S", "kind:verification,state:waiting", parent=intent_id)
    record_run(["dep", "add", verif_id, story_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "reopened"
    assert "cut" not in _labels_of(story_id)
    assert record_show_item(code_id)["state"] == "waiting"
    assert record_show_item(test_id)["state"] == "waiting"


def test_unlabelled_story_untouched(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    intent_id = _create("Intent I", "kind:intent,state:waiting")
    story_id = _create("Story S", "kind:story,state:waiting", parent=intent_id)
    code_id = _create("Story S code", "kind:code,state:waiting", parent=story_id)
    test_id = _create("Story S test", "kind:test,state:waiting", parent=story_id)
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "waiting"
    assert record_show_item(code_id)["state"] == "waiting"
    assert record_show_item(test_id)["state"] == "waiting"


def test_ready_story_advances_when_jobs_done(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    code_id = _create("Story S code", "kind:code,state:done", parent=story_id)
    test_id = _create("Story S test", "kind:test,state:done", parent=story_id)
    record_run(["dep", "add", test_id, code_id, "-t", "validates"])

    prove_once(config_path)

    assert record_show_item(story_id)["state"] == "checking"
