from ready_apply.ready_apply import ready_apply

from log_read_item.log_read_item import log_read_item
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _setup():
    story = record_run(
        [
            "create",
            "S",
            "-t",
            "task",
            "--no-inherit-labels",
            "-l",
            "kind:story,state:in_progress",
        ]
    )["id"]
    record_run(["update", story, "--acceptance", "1. x [testing]"])
    record_run(["label", "add", story, "cut"])
    code = record_run(
        [
            "create",
            "C",
            "-t",
            "task",
            "--no-inherit-labels",
            "-l",
            "kind:code,state:waiting",
            "--parent",
            story,
        ]
    )["id"]
    test = record_run(
        [
            "create",
            "T",
            "-t",
            "task",
            "--no-inherit-labels",
            "-l",
            "kind:test,state:waiting",
            "--parent",
            story,
        ]
    )["id"]
    return story, code, test


def _gathered(jobs, usage):
    return {"graph": record_graph(), "jobs": list(jobs), "usage": dict(usage)}


def _state(item_id):
    return record_graph()[item_id]["state"]


def _labels(item_id):
    labels = record_run(["label", "list", item_id])
    return [x if isinstance(x, str) else x.get("name", "") for x in labels]


def _texts(item_id):
    row = record_run(["show", item_id])[0]
    comments = row.get("comments", []) or []
    return [c.get("text", "") if isinstance(c, dict) else str(c) for c in comments]


def test_pass_sets_jobs_ready(fake_bd):
    story, code, test = _setup()
    ready_apply(story, [], _gathered([code, test], {}))
    assert _state(code) == "ready"
    assert _state(test) == "ready"


def test_pass_sets_story_ready(fake_bd):
    story, code, test = _setup()
    result = ready_apply(story, [], _gathered([code, test], {}))
    assert result == "ready"
    assert _state(story) == "ready"


def test_pass_logs_event_with_usage(fake_bd):
    story, code, test = _setup()
    usage = {
        "tokens": 5,
        "seconds": 1.5,
        "cost_usd": 0.1,
        "turns": 3,
        "harness": "h",
        "model": "m",
    }
    ready_apply(story, [], _gathered([code, test], usage))
    events = log_read_item(story)
    assert len(events) == 1
    event = events[0]
    assert event["gate"] == "ready"
    assert event["rule"] == "pass"
    assert event["tokens"] == 5
    assert event["usd"] == 0.1
    assert event["turns"] == 3
    assert event["inputs"]["harness"] == "h"
    assert event["inputs"]["model"] == "m"


def test_pass_without_usage_logs_minus_one(fake_bd):
    story, code, test = _setup()
    ready_apply(story, [], _gathered([code, test], {}))
    events = log_read_item(story)
    assert len(events) == 1
    assert events[0]["tokens"] == -1
    assert events[0]["usd"] is None
    assert events[0]["turns"] is None


def test_fail_reopens_and_removes_label(fake_bd):
    story, code, test = _setup()
    result = ready_apply(story, ["no_checklist"], _gathered([code, test], {}))
    assert result == "reopened"
    assert _state(story) == "reopened"
    assert "cut" not in _labels(story)


def test_fail_notes_and_logs_rules(fake_bd):
    story, code, test = _setup()
    rules = ["no_checklist", "sheet_no_cases"]
    ready_apply(story, rules, _gathered([code, test], {}))
    assert "ready: no_checklist,sheet_no_cases" in _texts(story)
    events = log_read_item(story)
    assert len(events) == 1
    assert events[0]["rule"] == "no_checklist,sheet_no_cases"


def test_fail_leaves_jobs_waiting(fake_bd):
    story, code, test = _setup()
    ready_apply(story, ["no_checklist"], _gathered([code, test], {}))
    assert _state(code) == "waiting"
    assert _state(test) == "waiting"
