import pathlib

from board_config.board_config import board_config
from column_of.column_of import column_of
from prove_once.prove_once import prove_once
from record_add_link.record_add_link import record_add_link
from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run
from record_set_sheet.record_set_sheet import record_set_sheet
from record_show_item.record_show_item import record_show_item

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_SHIPPED_CONFIG = str(_ROOT / "roles" / "board.toml")


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


def test_ordinary_pass_promotes_job_when_last_need_done(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    need_id = _create("Need code", "kind:code,state:done", parent=story_id)
    job_id = _create("Blocked code", "kind:code,state:waiting", parent=story_id)
    record_run(["dep", "add", job_id, "--blocked-by", need_id])

    result = prove_once(config_path)

    assert result == []
    assert record_show_item(job_id)["state"] == "ready"
    assert record_show_item(story_id)["state"] == "ready"


def test_intent_advances_when_every_story_is_done(fake_bd, tmp_path):
    """An Intent whose Stories are all verified goes to the Board's column on
    its own; before 2026-09-09 someone had to set it by hand."""
    config_path = _config(tmp_path)
    intent_id = _create("Intent I", "kind:intent,state:in_progress")
    done_id = _create("Story A", "kind:story,state:done", parent=intent_id)
    open_id = _create("Story B", "kind:story,state:checking", parent=intent_id)

    prove_once(config_path)
    assert record_show_item(intent_id)["state"] == "in_progress"

    record_run(["update", open_id, "--remove-label", "state:checking"])
    record_run(["update", open_id, "--add-label", "state:done"])
    prove_once(config_path)
    assert record_show_item(intent_id)["state"] == "checking"
    assert record_show_item(done_id)["state"] == "done"


def test_ordinary_pass_leaves_job_waiting_when_need_unmet(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    blocker_id = _create("Blocker code", "kind:code,state:waiting", parent=story_id)
    job_id = _create("Blocked code", "kind:code,state:waiting", parent=story_id)
    record_run(["dep", "add", job_id, "--blocked-by", blocker_id])

    result = prove_once(config_path)

    assert result == []
    assert record_show_item(job_id)["state"] == "waiting"
    assert record_show_item(story_id)["state"] == "ready"


def test_ordinary_pass_removes_ready_from_job_with_unmet_need(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:ready")
    blocker_id = _create("Blocker code", "kind:code,state:waiting", parent=story_id)
    job_id = _create("Stale code", "kind:code,state:ready", parent=story_id)
    record_run(["dep", "add", job_id, "--blocked-by", blocker_id])

    result = prove_once(config_path)

    assert result == []
    assert record_show_item(job_id)["state"] == "waiting"
    assert record_show_item(story_id)["state"] == "ready"


def test_ordinary_pass_leaves_job_waiting_under_an_ungated_story(fake_bd, tmp_path):
    """A Story the Ready gate has not released must not have its jobs promoted.

    Seen live on 2026-09-08: a smoke Story sat at waiting with no ready gate
    event while a Builder was already running one of its jobs, because the
    job's needs were trivially met. That is a gate bypass, not a promotion.
    """
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:waiting")
    job_id = _create("Free code", "kind:code,state:waiting", parent=story_id)

    prove_once(config_path)

    assert record_show_item(job_id)["state"] == "waiting"


def test_a_story_still_being_cut_does_not_release_its_jobs(fake_bd, tmp_path):
    """A Story the Engineer holds is in_progress and its sheets are not gated yet."""
    config_path = _config(tmp_path)
    story_id = _create("Story S", "kind:story,state:in_progress")
    need_id = _create("Need code", "kind:code,state:done", parent=story_id)
    job_id = _create("Blocked code", "kind:code,state:waiting", parent=story_id)
    record_run(["dep", "add", job_id, "--blocked-by", need_id])

    prove_once(config_path)

    assert record_show_item(job_id)["state"] == "waiting"


def _sheets(folder, cases, removed=()):
    code = "\n".join(
        [
            "# Instruction sheet",
            "- **Job id**: c",
            "- **Kind**: code",
            "- **Parent Story**: s",
            f"- **Function name**: `{folder}`",
            f"- **Folder**: `src/{folder}/`",
            "- **Signature**: `f() -> None`",
            "- **Inputs**: x.",
            "- **Outputs**: Return an empty list.",
            "- **Change**: rewrite",
        ]
    )
    lines = [
        "# Instruction sheet",
        "- **Job id**: t",
        "- **Kind**: test",
        "- **Parent Story**: s",
        f"- **Function name**: `{folder}`",
        f"- **Folder**: `src/{folder}/`",
        "- **Signature**: `f() -> None`",
        "- **Inputs**: x.",
        "- **Outputs**: Return an empty list.",
        "- **Cases**:",
    ]
    for name in cases:
        lines.append(f"  - `{name}`: works")
    for name in removed:
        lines.append(f"  - `{name}`: removed, no longer needed")
    return code, "\n".join(lines)


def _cut_story(folder, cases, removed=()):
    intent = record_create_item("intent", "Intent", "e")
    story = record_create_item("story", "Story S", "e", intent["id"])
    record_run(["label", "add", story["id"], "cut"])
    record_run(["update", story["id"], "--acceptance", "1. x [testing]"])
    record_create_item("verification", "Verify", "e", story["id"])
    code = record_create_item("code", f"{folder} code", "e", story["id"])
    test = record_create_item("test", f"{folder} test", "e", code["id"])
    record_add_link("needs_first", code["id"], test["id"])
    code_sheet, test_sheet = _sheets(folder, cases, removed)
    record_set_sheet(code["id"], code_sheet)
    record_set_sheet(test["id"], test_sheet)

    src = pathlib.Path.cwd() / "src" / folder
    src.mkdir(parents=True)
    (src / f"{folder}.py").write_text(f"def {folder}():\n    return []\n")
    (src / f"test_{folder}.py").write_text(
        "def test_first():\n    pass\n\n\ndef test_second():\n    pass\n"
    )
    return story["id"], code["id"], test["id"]


def test_ready_gate_refuses_omitted_existing_test_end_to_end(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story, code, test = _cut_story("alpha", ["test_first"])

    prove_once(config_path)

    assert record_show_item(story)["state"] == "waiting"
    note = record_run(["comments", story])[-1]["text"]
    assert "sheet_existing_case_missing:test_second" in note
    assert "cut" not in record_run(["show", story])[0]["labels"]
    assert record_show_item(code)["state"] != "ready"
    assert record_show_item(test)["state"] != "ready"


def test_ready_gate_accepts_kept_existing_test_end_to_end(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story, code, test = _cut_story("alpha", ["test_first", "test_second"])

    prove_once(config_path)

    assert record_show_item(story)["state"] == "ready"
    assert record_show_item(test)["state"] == "ready"


def test_ready_gate_accepts_removed_existing_test_end_to_end(fake_bd, tmp_path):
    config_path = _config(tmp_path)
    story, code, test = _cut_story("alpha", ["test_first"], removed=["test_second"])

    prove_once(config_path)

    assert record_show_item(story)["state"] == "ready"
    assert record_show_item(test)["state"] == "ready"


def test_bounce_note_routes_to_engineer_queue(fake_bd, tmp_path):
    job_id = _create("blocked code", "kind:code,state:checking")
    folder = "blocked"
    src = pathlib.Path.cwd() / "src" / folder
    src.mkdir(parents=True)
    (src / f"{folder}.py").write_text("import os\n")

    prove_once(_SHIPPED_CONFIG)

    rows = record_run(["show", job_id])
    row = rows[0] if isinstance(rows, list) else rows
    note_id = next(
        dep["id"]
        for dep in row.get("dependents", [])
        if dep.get("dependency_type") == "parent-child"
        and "kind:note" in dep.get("labels", [])
    )
    note = record_show_item(note_id)
    assert note["owner"] == "engineer"
    assert "- **For**: engineer" in note["sheet"]
    labels = record_run(["show", note_id])[0].get("labels", [])
    config = board_config(_SHIPPED_CONFIG)
    assert column_of(note, labels, config) == "engineer_notes"
