from datetime import datetime, timedelta

from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from release_dead_claims.release_dead_claims import release_dead_claims


def _job(state, claimant, kind="code"):
    args = ["create", "w " + kind, "-t", "task", "-l", f"kind:{kind},state:{state}"]
    args += ["--no-inherit-labels", "-a", claimant]
    return record_run(args)["id"]


def _offset(item_id, seconds):
    updated = record_run(["show", item_id])[0]["updated_at"]
    when = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    when += timedelta(seconds=seconds)
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_dead_claim_released_for_non_in_progress_states(fake_bd):
    ids = {
        state: _job(state, "builder-99999")
        for state in ("ready", "waiting", "checking", "blocked")
    }
    released = release_dead_claims(record_graph(), {"1"})
    assert set(released) == set(ids.values())
    graph = record_graph()
    for state, item_id in ids.items():
        assert graph[item_id]["claimed_by"] == ""
        assert graph[item_id]["state"] == state


def test_only_in_progress_claim_moves_to_ready(fake_bd):
    code_job = _job("in_progress", "builder-99999", kind="code")
    test_job = _job("in_progress", "builder-99999", kind="test")
    released = release_dead_claims(record_graph(), {"1"})
    assert set(released) == {code_job, test_job}
    graph = record_graph()
    assert graph[code_job]["claimed_by"] == "" and graph[code_job]["state"] == "ready"
    assert graph[test_job]["claimed_by"] == "" and graph[test_job]["state"] == "ready"


def test_live_pid_kept_inside_timeout(fake_bd):
    job = _job("in_progress", "builder-4242")
    now = _offset(job, 600)
    assert release_dead_claims(record_graph(), {"4242"}, 1800, now) == []
    graph = record_graph()
    assert graph[job]["claimed_by"] == "builder-4242"
    assert graph[job]["state"] == "in_progress"


def test_stale_live_pid_released(fake_bd):
    job = _job("in_progress", "builder-4242")
    now = _offset(job, 7200)
    assert release_dead_claims(record_graph(), {"4242"}, 1800, now) == [job]
    graph = record_graph()
    assert graph[job]["claimed_by"] == "" and graph[job]["state"] == "ready"


def test_person_empty_and_missing_claims_untouched(fake_bd):
    person = _job("in_progress", "fable")
    empty = _job("in_progress", "")
    assert release_dead_claims(record_graph(), set()) == []
    graph = record_graph()
    assert graph[person]["claimed_by"] == "fable"
    assert graph[empty]["claimed_by"] == ""
