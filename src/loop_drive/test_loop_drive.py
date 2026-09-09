import pathlib
import subprocess

from loop_drive.loop_drive import loop_drive

from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

_BOARD_TOML = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _config():
    return str(_BOARD_TOML)


def _snapshots(result):
    assert isinstance(result, list)
    assert result
    return result


def _story_snapshot(snapshot):
    for key in ("story", "story_state"):
        if key in snapshot:
            return snapshot[key]
    raise AssertionError(f"snapshot has no story state: {snapshot!r}")


def _items(snapshot):
    for key in ("items", "state"):
        value = snapshot.get(key)
        if isinstance(value, dict):
            return value
    raise AssertionError(f"snapshot has no item state: {snapshot!r}")


def _subjects(repo):
    result = subprocess.run(
        ["git", "log", "--format=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def _job_states(snapshot):
    return [
        value.get("state", value)
        for value in _items(snapshot).values()
        if isinstance(value, dict) and value.get("kind") in ("code", "test")
    ]


def test_loop_drive_walks_pipeline_and_snapshots(fake_bd, monkeypatch):
    monkeypatch.chdir(fake_bd)
    result = loop_drive(
        "intent-1",
        _config(),
        str(fake_bd),
        {"functions": ["alpha", "beta"]},
        {"alpha": {}, "beta": {}},
    )

    snapshots = _snapshots(result)
    assert [snapshot["step"] for snapshot in snapshots] == [
        "engineer",
        "ready",
        "build_alpha",
        "prove_alpha",
        "build_beta",
        "prove_beta",
    ]
    final = snapshots[-1]
    assert _story_snapshot(final) == "checking"
    assert _job_states(final) and all(state == "done" for state in _job_states(final))
    subjects = final.get("git_log", final.get("commits"))
    assert subjects is not None
    assert len(subjects) == 2
    assert all("job" in subject for subject in subjects)


def test_loop_drive_refuses_missing_change_sheet(fake_bd, monkeypatch):
    monkeypatch.chdir(fake_bd)
    result = loop_drive(
        "intent-2",
        _config(),
        str(fake_bd),
        {"functions": ["alpha"], "faults": {"alpha": "no_change"}},
        {"alpha": {}},
    )

    final = _snapshots(result)[-1]
    assert _story_snapshot(final) == "waiting"
    assert "cut" not in final.get("story_labels", final.get("labels", []))
    assert "sheet_exists_without_change" in final.get("notes", "")
    assert not any(state == "ready" for state in _job_states(final))
    assert _subjects(fake_bd) == []


def test_loop_drive_bounces_second_folder_builder(fake_bd, monkeypatch):
    monkeypatch.chdir(fake_bd)
    result = loop_drive(
        "intent-3",
        _config(),
        str(fake_bd),
        {"functions": ["alpha"]},
        {"alpha": {"fault": "second_folder"}},
    )

    final = _snapshots(result)[-1]
    assert _story_snapshot(final) in ("ready", "checking")
    assert "file_outside_folder" in final.get("notes", "")
    assert _subjects(fake_bd) == []


def test_loop_drive_blocks_after_three_builder_raises(fake_bd, monkeypatch):
    monkeypatch.chdir(fake_bd)
    result = loop_drive(
        "intent-4",
        _config(),
        str(fake_bd),
        {"functions": ["alpha"]},
        {"alpha": {"fault": "raise"}},
    )

    final = _snapshots(result)[-1]
    assert "blocked" in set(final.get("job_states", {}).values())
    assert "released three times" in final.get("notes", "")
    assert _subjects(fake_bd) == []


def test_loop_drive_skips_jobs_under_blocked_story(fake_bd, monkeypatch):
    monkeypatch.chdir(fake_bd)
    result = loop_drive(
        "intent-5",
        _config(),
        str(fake_bd),
        {"functions": ["alpha"]},
        {"alpha": {"block_after_ready": True}},
    )

    final = _snapshots(result)[-1]
    story_id = final["story_id"]
    record_set_state(story_id, "blocked")
    before = record_run(["list", "--all", "--exclude-type", "event"])
    loop_drive(
        "intent-5",
        _config(),
        str(fake_bd),
        {"functions": [], "skip_mint": True},
        {},
    )
    after = record_run(["list", "--all", "--exclude-type", "event"])
    assert [row for row in after if row.get("assignee")] == [
        row for row in before if row.get("assignee")
    ]
