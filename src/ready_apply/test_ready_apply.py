from ready_apply.ready_apply import ready_apply
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _create(title, labels, parent=None):
    args = ["create", title, "-t", "task", "--no-inherit-labels", "-l", labels]
    if parent:
        args += ["--parent", parent]
    return record_run(args)["id"]


def _story():
    story = _create("S", "kind:story,state:waiting")
    record_run(["update", story, "--acceptance", "1. x [testing]"])
    return story


def _gathered(jobs):
    return {"graph": record_graph(), "jobs": list(jobs), "usage": {}}


def test_pass_sets_job_ready_without_needs(fake_bd):
    story = _story()
    code = _create("C code", "kind:code,state:waiting", parent=story)
    result = ready_apply(story, [], _gathered([code]))
    assert result == "ready"
    assert record_graph()[code]["state"] == "ready"


def test_pass_leaves_job_waiting_when_need_unmet(fake_bd):
    story = _story()
    blocker = _create("B code", "kind:code,state:waiting", parent=story)
    blocked = _create("C code", "kind:code,state:waiting", parent=story)
    record_run(["dep", "add", blocked, "--blocked-by", blocker])
    result = ready_apply(story, [], _gathered([blocker, blocked]))
    assert result == "ready"
    assert record_graph()[blocked]["state"] == "waiting"


def test_pass_leaves_done_job_done(fake_bd):
    story = _story()
    done = _create("Old code", "kind:code,state:done", parent=story)
    fresh = _create("New code", "kind:code,state:waiting", parent=story)
    result = ready_apply(story, [], _gathered([done, fresh]))
    assert result == "ready"
    assert record_graph()[done]["state"] == "done"


def test_fail_returns_the_story_to_the_engineer(fake_bd):
    story = _story()
    record_run(["label", "add", story, "cut"])
    code = _create("C code", "kind:code,state:waiting", parent=story)
    result = ready_apply(story, ["sheet_exists_without_change"], _gathered([code]))
    assert result == "waiting"
    row = record_run(["show", story])[0]
    assert "state:waiting" in row["labels"]
    assert "cut" not in row["labels"]
    assert row["comments"][-1]["text"] == "ready: sheet_exists_without_change"


def test_fail_takes_ready_away_from_every_job(fake_bd):
    story = _story()
    ready = _create("A code", "kind:code,state:ready", parent=story)
    done = _create("B code", "kind:code,state:done", parent=story)
    ready_apply(story, ["sheet_missing"], _gathered([ready, done]))
    assert record_graph()[ready]["state"] == "waiting"
    assert record_graph()[done]["state"] == "done"
