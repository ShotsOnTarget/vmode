from datetime import datetime, timedelta

from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from release_dead_claims.release_dead_claims import release_dead_claims


def _job(state, claimant, kind="code"):
    args = ["create", "w code", "-t", "task", "-l", f"kind:{kind},state:{state}"]
    args += ["--no-inherit-labels", "-a", claimant]
    return record_run(args)["id"]


def _now_after(item_id, seconds):
    updated = record_run(["show", item_id])[0]["updated_at"]
    when = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    when += timedelta(seconds=seconds)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_dead_pid_released_from_non_in_progress_states(fake_bd):
    jobs = {
        state: _job(state, "builder-99999")
        for state in ("ready", "waiting", "checking", "blocked")
    }
    assert release_dead_claims(record_graph(), {"1"}) == list(jobs.values())
    graph = record_graph()
    for state, job in jobs.items():
        assert graph[job]["claimed_by"] == "" and graph[job]["state"] == state


def test_dead_pid_released_from_in_progress_state(fake_bd):
    job = _job("in_progress", "builder-99999")
    assert release_dead_claims(record_graph(), {"1"}) == [job]
    graph = record_graph()
    assert graph[job]["claimed_by"] == "" and graph[job]["state"] == "ready"


def test_alive_pid_kept_inside_timeout(fake_bd):
    job = _job("in_progress", "builder-4242")
    now = _now_after(job, 0)
    assert release_dead_claims(record_graph(), {"4242"}, now=now) == []
    graph = record_graph()
    assert graph[job]["claimed_by"] == "builder-4242"
    assert graph[job]["state"] == "in_progress"


def test_live_pid_released_after_timeout(fake_bd):
    job = _job("in_progress", "builder-4242")
    now = _now_after(job, 7200)
    assert release_dead_claims(record_graph(), {"4242"}, 1800, now) == [job]
    graph = record_graph()
    assert graph[job]["claimed_by"] == "" and graph[job]["state"] == "ready"


def test_person_claim_kept(fake_bd):
    job = _job("in_progress", "fable")
    assert release_dead_claims(record_graph(), set()) == []
    assert record_graph()[job]["claimed_by"] == "fable"


def test_empty_claim_kept(fake_bd):
    job = _job("in_progress", "")
    assert release_dead_claims(record_graph(), set()) == []
    assert record_graph()[job]["claimed_by"] == ""
