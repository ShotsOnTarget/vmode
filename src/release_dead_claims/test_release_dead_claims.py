from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from release_dead_claims.release_dead_claims import release_dead_claims


def _job(state, claimant):
    args = ["create", "w code", "-t", "task", "-l", f"kind:code,state:{state}"]
    args += ["--no-inherit-labels", "-a", claimant]
    return record_run(args)["id"]


def test_dead_pid_released(bd_repo):
    job = _job("in_progress", "builder-99999")
    assert release_dead_claims(record_graph(), {"1"}) == [job]
    graph = record_graph()
    assert graph[job]["claimed_by"] == "" and graph[job]["state"] == "ready"


def test_alive_pid_kept(bd_repo):
    job = _job("in_progress", "builder-4242")
    assert release_dead_claims(record_graph(), {"4242"}) == []
    assert record_graph()[job]["claimed_by"] == "builder-4242"


def test_person_kept(bd_repo):
    job = _job("in_progress", "fable")
    assert release_dead_claims(record_graph(), set()) == []
    assert record_graph()[job]["claimed_by"] == "fable"
