from datetime import datetime, timedelta

from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from release_dead_claims.release_dead_claims import release_dead_claims


def _job(state, claimant, kind="code"):
    args = ["create", "w code", "-t", "task", "-l", f"kind:{kind},state:{state}"]
    args += ["--no-inherit-labels", "-a", claimant]
    return record_run(args)["id"]


def _offset(item_id, seconds):
    updated = record_run(["show", item_id])[0]["updated_at"]
    when = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    when += timedelta(seconds=seconds)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_dead_pid_released(fake_bd):
    job = _job("in_progress", "builder-99999")
    assert release_dead_claims(record_graph(), {"1"}) == [job]
    graph = record_graph()
    assert graph[job]["claimed_by"] == "" and graph[job]["state"] == "ready"


def test_alive_pid_kept(fake_bd):
    job = _job("in_progress", "builder-4242")
    assert release_dead_claims(record_graph(), {"4242"}) == []
    assert record_graph()[job]["claimed_by"] == "builder-4242"


def test_person_kept(fake_bd):
    job = _job("in_progress", "fable")
    assert release_dead_claims(record_graph(), set()) == []
    assert record_graph()[job]["claimed_by"] == "fable"


def test_dead_story_claim_in_progress_released(fake_bd):
    story = _job("in_progress", "analyst-99999", kind="story")
    assert release_dead_claims(record_graph(), {"1"}) == [story]
    graph = record_graph()
    assert graph[story]["claimed_by"] == "" and graph[story]["state"] == "done"


def test_done_job_untouched(fake_bd):
    job = _job("done", "builder-99999")
    assert release_dead_claims(record_graph(), {"1"}) == []
    graph = record_graph()
    assert graph[job]["claimed_by"] == "builder-99999" and graph[job]["state"] == "done"


def test_ready_job_untouched(fake_bd):
    job = _job("ready", "builder-99999")
    assert release_dead_claims(record_graph(), {"1"}) == []
    graph = record_graph()
    assert (
        graph[job]["claimed_by"] == "builder-99999" and graph[job]["state"] == "ready"
    )


def test_live_pid_released_when_claim_is_older_than_the_timeout(fake_bd):
    job = _job("in_progress", "builder-4242")
    now = _offset(job, 7200)
    assert release_dead_claims(record_graph(), {"4242"}, 1800, now) == [job]
    graph = record_graph()
    assert graph[job]["claimed_by"] == "" and graph[job]["state"] == "ready"


def test_live_pid_kept_inside_the_timeout(fake_bd):
    job = _job("in_progress", "builder-4242")
    now = _offset(job, 600)
    assert release_dead_claims(record_graph(), {"4242"}, 1800, now) == []
    assert record_graph()[job]["claimed_by"] == "builder-4242"


def test_unknown_kind_keeps_its_state(fake_bd):
    item = _job("in_progress", "builder-99999", kind="verification")
    assert release_dead_claims(record_graph(), {"1"}) == [item]
    graph = record_graph()
    assert graph[item]["claimed_by"] == "" and graph[item]["state"] == "in_progress"
