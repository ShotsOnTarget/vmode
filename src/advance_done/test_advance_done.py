from advance_done.advance_done import advance_done
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _item(title, labels, parent=None, assignee=""):
    args = ["create", title, "-t", "task", "-l", labels, "--no-inherit-labels"]
    if parent:
        args += ["--parent", parent]
    if assignee:
        args += ["-a", assignee]
    return record_run(args)["id"]


def test_story_with_every_job_done_goes_to_checking(fake_bd):
    story = _item("S", "kind:story,state:ready")
    _item("f code", "kind:code,state:done", story)
    _item("f test", "kind:test,state:done", story)
    assert advance_done(record_graph()) == [story]
    assert record_show_item(story)["state"] == "checking"


def test_story_with_a_job_open_is_left_alone(fake_bd):
    story = _item("S", "kind:story,state:ready")
    _item("f code", "kind:code,state:done", story)
    _item("f test", "kind:test,state:checking", story)
    assert advance_done(record_graph()) == []
    assert record_show_item(story)["state"] == "ready"


def test_intent_with_every_story_done_goes_to_checking(fake_bd):
    intent = _item("I", "kind:intent,state:in_progress")
    _item("S1", "kind:story,state:done", intent)
    _item("S2", "kind:story,state:done", intent)
    assert advance_done(record_graph()) == [intent]
    assert record_show_item(intent)["state"] == "checking"


def test_intent_with_a_story_open_or_a_claim_is_left_alone(fake_bd):
    intent = _item("I", "kind:intent,state:in_progress")
    _item("S1", "kind:story,state:done", intent)
    open_story = _item("S2", "kind:story,state:checking", intent)
    assert advance_done(record_graph()) == []
    record_run(["update", open_story, "--remove-label", "state:checking"])
    record_run(["update", open_story, "--add-label", "state:done"])
    record_run(["update", intent, "-a", "architect"])
    assert advance_done(record_graph()) == []
    assert record_show_item(intent)["state"] == "in_progress"


def test_a_parent_with_no_children_stays(fake_bd):
    intent = _item("I", "kind:intent,state:in_progress")
    story = _item("S", "kind:story,state:waiting", intent)
    assert advance_done(record_graph()) == []
    assert record_show_item(story)["state"] == "waiting"
