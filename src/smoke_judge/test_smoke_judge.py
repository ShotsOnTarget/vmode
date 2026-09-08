from smoke_judge.smoke_judge import smoke_judge

from log_append.log_append import log_append
from pipeline_run_count.pipeline_run_count import pipeline_run_count
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_set_checklist.record_set_checklist import record_set_checklist
from record_set_sheet.record_set_sheet import record_set_sheet
from record_set_state.record_set_state import record_set_state


def _intent():
    return record_create_item("intent", "standing", "board")["id"]


def _story(intent_id, target):
    story_id = record_create_item("story", "smoke run", "board", intent_id)["id"]
    record_set_checklist(story_id, [f"run count is {target} [testing]"])
    record_set_sheet(story_id, f"smoke run for target {target}: pipeline_run_count")
    return story_id


def _pair(story_id):
    code_id = record_create_item("code", "fn code", "supervisor", story_id)["id"]
    test_id = record_create_item("test", "fn test", "supervisor", code_id)["id"]
    return code_id, test_id


def _event(item_id, gate, inputs=None):
    log_append(
        {
            "item": item_id,
            "gate": gate,
            "rule": "r",
            "inputs": {} if inputs is None else inputs,
            "state": "s",
            "tokens": 0,
            "seconds": 0,
            "actor": "supervisor",
        }
    )


def _passed(result):
    for key in ("pass", "passed", "ok", "success"):
        if key in result:
            value = result[key]
            if isinstance(value, str):
                return value.lower() in ("pass", "passed", "true", "ok", "success")
            return bool(value)
    for key in ("result", "status", "outcome", "verdict"):
        if key in result:
            value = result[key]
            if isinstance(value, bool):
                return value
            return str(value).lower() in ("pass", "passed", "ok", "success")
    raise AssertionError(f"result names no pass/fail: {result!r}")


def _version(result):
    for key in ("version", "produced_version", "run_count", "target", "target_count"):
        if key in result:
            return result[key]
    raise AssertionError(f"result names no version: {result!r}")


def _bounces(result):
    for key in ("bounces", "bounce_count", "bounce", "bounced"):
        if key in result:
            return result[key]
    raise AssertionError(f"result names no bounce count: {result!r}")


def _stall(result):
    for key in ("stall", "stalled", "stopped", "where", "location"):
        if key in result and isinstance(result[key], dict):
            return result[key]
    raise AssertionError(f"result names no stall object: {result!r}")


def _stall_column(stall):
    for key in ("column", "col", "board_column"):
        if key in stall:
            return stall[key]
    raise AssertionError(f"stall names no column: {stall!r}")


def _stall_item(stall):
    for key in ("item", "item_id", "id", "job", "job_id"):
        if key in stall:
            return stall[key]
    raise AssertionError(f"stall names no item id: {stall!r}")


def _stall_state(stall):
    for key in ("state", "status"):
        if key in stall:
            return stall[key]
    raise AssertionError(f"stall names no state: {stall!r}")


def test_passes_finished_run_and_reports_version(fake_bd):
    target = pipeline_run_count()
    story_id = _story(_intent(), target)
    code_id, test_id = _pair(story_id)
    record_set_state(code_id, "done")
    record_set_state(test_id, "done")
    record_set_state(story_id, "checking")
    _event(story_id, "ready")
    _event(code_id, "built")
    _event(test_id, "proven")
    result = smoke_judge(story_id, 5.0)
    assert _passed(result) is True
    assert str(_version(result)) == str(target)
    assert int(_bounces(result)) == 0


def test_reports_stalled_item_at_timeout(fake_bd):
    story_id = _story(_intent(), pipeline_run_count())
    code_id, test_id = _pair(story_id)
    record_set_state(story_id, "ready")
    record_set_state(code_id, "ready")
    _event(story_id, "ready")
    result = smoke_judge(story_id, 0.05)
    assert _passed(result) is False
    stall = _stall(result)
    column = _stall_column(stall)
    assert isinstance(column, str) and column
    item_id = _stall_item(stall)
    graph = record_graph()
    assert item_id in graph
    assert _stall_state(stall) == graph[item_id]["state"]
    assert graph[item_id]["state"] != "done"
    assert test_id in graph


def test_reports_bounces_without_failing_success(fake_bd):
    target = pipeline_run_count()
    story_id = _story(_intent(), target)
    code_id, test_id = _pair(story_id)
    record_set_state(code_id, "done")
    record_set_state(test_id, "done")
    record_set_state(story_id, "checking")
    _event(story_id, "ready")
    _event(code_id, "built", {"action": "bounce"})
    _event(code_id, "built", {"action": "bounce"})
    _event(code_id, "built")
    _event(test_id, "proven")
    result = smoke_judge(story_id, 5.0)
    assert _passed(result) is True
    assert int(_bounces(result)) == 2
    assert str(_version(result)) == str(target)


def test_fails_when_the_run_wrote_a_different_count(fake_bd, monkeypatch):
    target = pipeline_run_count()
    story_id = _story(_intent(), target)
    code_id, test_id = _pair(story_id)
    record_set_state(code_id, "done")
    record_set_state(test_id, "done")
    record_set_state(story_id, "checking")
    _event(story_id, "ready")
    _event(code_id, "built")
    _event(test_id, "proven")
    monkeypatch.setattr("smoke_judge.smoke_judge.count_written", lambda: target - 1)

    result = smoke_judge(story_id, 5.0)

    assert _passed(result) is False
    assert result["count"] == {"asked": target, "wrote": target - 1}
