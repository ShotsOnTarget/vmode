import copy

import pytest

from log_append.log_append import log_append
from record_graph.record_graph import record_graph
from record_labels.record_labels import record_labels
from record_run.record_run import record_run
from story_status.story_status import story_status


def _item(
    item_id, kind, parent=None, checks=None, state="ready", claimed_by="", title=""
):
    return {
        "id": item_id,
        "kind": kind,
        "title": title,
        "owner": "builder",
        "state": state,
        "parent": parent,
        "checks": checks or [],
        "needs": [],
        "claimed_by": claimed_by,
    }


def _story_graph(state="ready"):
    return {
        "s1": _item("s1", "story", state=state),
        "c1": _item(
            "c1",
            "code",
            parent="s1",
            state="done",
            claimed_by="builder-1",
            title="widget code",
        ),
        "t1": _item(
            "t1", "test", parent="s1", checks=["c1"], state="done", title="widget test"
        ),
    }


def _mk(title, **kw):
    args = ["create", title, "-a", "me", "--no-inherit-labels"]
    for flag, value in kw.items():
        args += [flag, value]
    created = record_run(args)
    return created[0]["id"] if isinstance(created, list) else created["id"]


def _event(item, gate, rule="pass", inputs=None, tokens=0, turns=0, usd=0.0):
    return {
        "item": item,
        "gate": gate,
        "rule": rule,
        "inputs": inputs if inputs is not None else {},
        "state": "done",
        "tokens": tokens,
        "seconds": 0.1,
        "actor": "supervisor",
        "usd": usd,
        "turns": turns,
    }


def test_one_entry_per_job(fake_bd):
    result = story_status("s1", _story_graph(), {})
    assert [job["id"] for job in result["jobs"]] == ["c1", "t1"]


def test_job_entry_fields(fake_bd):
    result = story_status("s1", _story_graph(), {})
    for job in result["jobs"]:
        assert set(job.keys()) == {
            "id",
            "kind",
            "function",
            "state",
            "retries",
            "claimed",
        }


def test_function_comes_from_the_title(fake_bd):
    result = story_status("s1", _story_graph(), {})
    functions = {job["id"]: job["function"] for job in result["jobs"]}
    assert functions == {"c1": "widget", "t1": "widget"}


def test_retries_from_the_retry_label(fake_bd):
    labels = {"c1": ["retry:2"]}
    result = story_status("s1", _story_graph(), labels)
    retries = {job["id"]: job["retries"] for job in result["jobs"]}
    assert retries == {"c1": 2, "t1": 0}


def test_claimed_reflects_the_claim(fake_bd):
    result = story_status("s1", _story_graph(), {})
    claimed = {job["id"]: job["claimed"] for job in result["jobs"]}
    assert claimed == {"c1": True, "t1": False}


def test_story_state_and_id(fake_bd):
    result = story_status("s1", _story_graph(state="blocked"), {})
    assert result["id"] == "s1"
    assert result["state"] == "blocked"


def test_one_line_per_gate_run(fake_bd):
    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    log_append(_event(story, "built"))
    log_append(_event(story, "proven"))
    log_append(_event(story, "ready"))
    result = story_status(story, record_graph(), record_labels())
    assert {run["gate"] for run in result["runs"]} == {"built", "proven", "ready"}
    assert len(result["runs"]) == 3


def test_run_entry_fields(fake_bd):
    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    inputs = {"retries": 1, "harness": "claude_code", "model": "claude-sonnet-5"}
    log_append(_event(story, "built", inputs=inputs, tokens=100, turns=5, usd=1.23))
    entry = story_status(story, record_graph(), record_labels())["runs"][0]
    assert set(entry.keys()) == {
        "item",
        "ts",
        "gate",
        "rule",
        "retries",
        "tokens",
        "turns",
        "usd",
        "harness",
        "model",
    }
    assert entry["item"] == story
    assert entry["gate"] == "built"
    assert entry["rule"] == "pass"
    assert entry["retries"] == 1
    assert entry["tokens"] == 100
    assert entry["turns"] == 5
    assert entry["usd"] == 1.23
    assert entry["harness"] == "claude_code"
    assert entry["model"] == "claude-sonnet-5"


def test_missing_run_fields_default(fake_bd):
    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    log_append(_event(story, "ready", inputs={}, turns=None, usd=None))
    entry = story_status(story, record_graph(), record_labels())["runs"][0]
    assert entry["retries"] == 0
    assert entry["usd"] == 0.0
    assert entry["turns"] == 0
    assert entry["harness"] == ""
    assert entry["model"] == ""


def test_other_gates_are_left_out(fake_bd):
    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    log_append(_event(story, "verified"))
    result = story_status(story, record_graph(), record_labels())
    assert result["runs"] == []


def test_duplicate_events_appear_once(fake_bd):
    from fake_record.fake_record import DB

    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    first = log_append(_event(story, "built"))
    second = log_append(_event(story, "built"))
    DB["items"][second]["created_at"] = DB["items"][first]["created_at"]
    result = story_status(story, record_graph(), record_labels())
    assert len(result["runs"]) == 1


def test_same_arguments_same_result(fake_bd):
    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    code = _mk("code1", **{"--parent": story, "-l": "kind:code,state:done"})
    log_append(_event(code, "built"))
    graph, labels = record_graph(), record_labels()
    assert story_status(story, graph, labels) == story_status(story, graph, labels)


def test_arguments_are_not_mutated(fake_bd):
    story = _mk("story1", **{"-l": "kind:story,state:ready"})
    code = _mk("code1", **{"--parent": story, "-l": "kind:code,state:done"})
    log_append(_event(code, "built"))
    graph, labels = record_graph(), record_labels()
    before_graph, before_labels = copy.deepcopy(graph), copy.deepcopy(labels)
    story_status(story, graph, labels)
    assert graph == before_graph
    assert labels == before_labels


def test_unknown_story_raises(fake_bd):
    with pytest.raises(ValueError):
        story_status("nope", _story_graph(), {})


def test_non_story_id_raises(fake_bd):
    with pytest.raises(ValueError):
        story_status("c1", _story_graph(), {})
