import pathlib
import subprocess

from loop_drive.loop_drive import loop_drive
from pull_once.pull_once import pull_once
from record_graph.record_graph import record_graph
from record_set_state.record_set_state import record_set_state
from scripted_builder.scripted_builder import scripted_builder

_BOARD_TOML = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _subjects(repo):
    result = subprocess.run(
        ["git", "log", "--format=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.splitlines() if result.returncode == 0 else []


def jobs(snapshot):
    return [state for state in snapshot["job_states"].values()]


def commits(snapshot):
    return [subject for subject in snapshot["git_log"] if "job vm-" in subject]


def _run(fake_bd, monkeypatch, intent_id, engineer_recipe, builder_recipes):
    monkeypatch.chdir(fake_bd)
    return loop_drive(
        intent_id,
        str(_BOARD_TOML),
        str(fake_bd),
        engineer_recipe,
        builder_recipes,
    )


def test_loop_drive_walks_pipeline_and_snapshots(fake_bd, monkeypatch):
    snapshots = _run(
        fake_bd,
        monkeypatch,
        "intent-1",
        {"functions": ["alpha", "beta"]},
        {"alpha": {}, "beta": {}},
    )

    assert all(
        set(snapshot)
        == {
            "step",
            "story_id",
            "story_state",
            "story_labels",
            "job_states",
            "git_log",
            "notes",
        }
        for snapshot in snapshots
    )
    steps = [snapshot["step"] for snapshot in snapshots]
    assert steps[:2] == ["engineer", "ready"]
    assert steps[2::2] and all(step == "build" for step in steps[2::2])
    assert steps[3::2] and all(step == "prove" for step in steps[3::2])
    assert steps[-1] == "prove"
    final = snapshots[-1]
    assert final["story_state"] == "checking"
    assert jobs(final) and all(state == "done" for state in jobs(final))
    assert len(commits(final)) == 4


def test_loop_drive_refuses_missing_change_sheet(fake_bd, monkeypatch):
    alpha = fake_bd / "src" / "alpha"
    alpha.mkdir(parents=True)
    (alpha / "alpha.py").write_text(
        'def alpha():\n    """Return the old value."""\n    return "old"\n',
        encoding="utf-8",
    )
    (alpha / "test_alpha.py").write_text(
        "from alpha.alpha import alpha\n\n\ndef test_alpha_old():\n"
        '    assert alpha() == "old"\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=fake_bd, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "-m",
            "alpha exists",
        ],
        cwd=fake_bd,
        check=True,
    )

    snapshots = _run(
        fake_bd,
        monkeypatch,
        "intent-2",
        {"functions": ["alpha"], "faults": {"alpha": "no_change"}},
        {"alpha": {}},
    )

    final = snapshots[-1]
    assert final["step"] == "ready"
    assert final["story_state"] == "waiting"
    assert "cut" not in final["story_labels"]
    assert "sheet_exists_without_change" in final["notes"]
    assert "ready" not in jobs(final)
    assert commits(final) == []


def test_loop_drive_bounces_second_folder_builder(fake_bd, monkeypatch):
    snapshots = _run(
        fake_bd,
        monkeypatch,
        "intent-3",
        {"functions": ["alpha"]},
        {"alpha": {"fault": "second_folder"}},
    )

    final = snapshots[-1]
    assert "file_outside_folder" in final["notes"]
    assert final["story_state"] != "checking"
    assert any(state != "done" for state in jobs(final))


def test_loop_drive_blocks_after_three_builder_raises(fake_bd, monkeypatch):
    snapshots = _run(
        fake_bd,
        monkeypatch,
        "intent-4",
        {"functions": ["alpha"]},
        {"alpha": {"fault": "raise"}},
    )

    final = snapshots[-1]
    assert "blocked" in jobs(final)
    assert "released 3 times" in final["notes"]
    assert commits(final) == []


def test_loop_drive_skips_jobs_under_blocked_story(fake_bd, monkeypatch):
    snapshots = _run(
        fake_bd,
        monkeypatch,
        "intent-5",
        {"functions": ["alpha"], "stop_after_ready": True},
        {"alpha": {}},
    )

    final = snapshots[-1]
    assert final["step"] == "ready"
    assert set(jobs(final)) == {"ready", "waiting"}
    story_id = final["story_id"]
    record_set_state(story_id, "blocked")
    before = {
        item_id: item["state"]
        for item_id, item in record_graph().items()
        if item.get("parent") == story_id
    }
    result = pull_once(
        "builder",
        str(_BOARD_TOML),
        lambda item, column: scripted_builder({**item, "recipe": {}}, column),
    )
    assert result == []
    after = {
        item_id: item["state"]
        for item_id, item in record_graph().items()
        if item.get("parent") == story_id
    }
    assert after == before
