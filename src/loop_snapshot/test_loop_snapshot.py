import subprocess

from loop_snapshot.loop_snapshot import loop_snapshot

from create_pair.create_pair import create_pair
from record_add_note.record_add_note import record_add_note
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels


def _seed():
    intent = record_create_item("intent", "the loop", "board")
    story = record_create_item("story", "one story", "architect", intent["id"])
    jobs = create_pair(story["id"], "alpha", "engineer")
    return story["id"], jobs


def test_keys_and_story_fields(fake_bd):
    story_id, _ = _seed()
    snap = loop_snapshot("ready", story_id, str(fake_bd))
    assert set(snap) == {
        "step",
        "story_id",
        "story_state",
        "story_labels",
        "job_states",
        "git_log",
        "notes",
    }
    assert snap["step"] == "ready"
    assert snap["story_id"] == story_id
    assert snap["story_state"] == "waiting"
    assert snap["story_labels"] == record_labels()[story_id]


def test_job_states_cover_every_job_under_the_story(fake_bd):
    story_id, jobs = _seed()
    snap = loop_snapshot("engineer", story_id, str(fake_bd))
    graph = record_graph()
    expected = {job_id: graph[job_id]["state"] for job_id in jobs.values()}
    assert snap["job_states"] == expected


def test_git_log_empty_without_commits(fake_bd):
    story_id, _ = _seed()
    snap = loop_snapshot("build_alpha", story_id, str(fake_bd))
    assert snap["git_log"] == []


def test_git_log_lists_subjects_after_a_commit(fake_bd):
    story_id, _ = _seed()
    subprocess.run(["git", "add", "-A"], cwd=str(fake_bd), check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "alpha: job x passed",
        ],
        cwd=str(fake_bd),
        check=True,
    )
    snap = loop_snapshot("build_alpha", story_id, str(fake_bd))
    assert snap["git_log"] == ["alpha: job x passed"]


def test_notes_join_comments_and_note_titles(fake_bd):
    story_id, jobs = _seed()
    record_add_note(story_id, "hello")
    record_create_item("note", "released 3 times", "supervisor", jobs["code"])
    snap = loop_snapshot("build_alpha", story_id, str(fake_bd))
    assert "hello" in snap["notes"]
    assert "released 3 times" in snap["notes"]
