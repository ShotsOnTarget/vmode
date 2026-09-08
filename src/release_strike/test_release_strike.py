from record_add_note.record_add_note import record_add_note
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from release_strike.release_strike import release_strike


def _job(labels="kind:code,state:in_progress"):
    return record_run(["create", "J", "-l", labels, "--no-inherit-labels"])["id"]


def _comments(item_id):
    return [c["text"] for c in record_run(["comments", item_id])]


def test_first_release_returns_the_prior_state(fake_bd):
    job = _job()
    assert release_strike(job, "ready", "boom") == "ready"
    assert record_graph()[job]["state"] == "ready"


def test_the_reason_is_kept_whole_up_to_a_thousand_characters(fake_bd):
    job = _job()
    release_strike(job, "ready", "x" * 1500)
    text = _comments(job)[-1]
    assert text.startswith("release: ")
    assert len(text) == len("release: ") + 1000


def test_third_release_in_a_row_blocks(fake_bd):
    job = _job()
    release_strike(job, "ready", "one")
    release_strike(job, "ready", "two")
    assert release_strike(job, "ready", "three") == "blocked"
    assert record_graph()[job]["state"] == "blocked"


def test_a_blocked_item_gets_a_note_for_the_architect(fake_bd):
    job = _job()
    for reason in ("one", "two", "three"):
        release_strike(job, "ready", reason)
    notes = [i for i in record_graph().values() if i["kind"] == "note"]
    assert len(notes) == 1
    assert notes[0]["parent"] == job
    assert notes[0]["owner"] == "supervisor"
    assert notes[0]["title"].startswith("released 3 times")
    assert _comments(notes[0]["id"])[-1].startswith("For: architect")


def test_a_finished_run_resets_the_count(fake_bd):
    job = _job()
    release_strike(job, "ready", "one")
    release_strike(job, "ready", "two")
    record_add_note(job, "usage: {}")
    assert release_strike(job, "ready", "three") == "ready"
    assert record_graph()[job]["state"] == "ready"


def test_two_releases_do_not_block(fake_bd):
    job = _job()
    release_strike(job, "waiting", "one")
    assert release_strike(job, "waiting", "two") == "waiting"
    assert not [i for i in record_graph().values() if i["kind"] == "note"]
