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
