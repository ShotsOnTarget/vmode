from smoke_story.smoke_story import smoke_story

from record_create_item.record_create_item import record_create_item
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _intent():
    return record_create_item("intent", "standing", "board")["id"]


def _story_id(result):
    for key in ("story_id", "id", "story"):
        if key in result:
            return result[key]
    raise AssertionError(f"result has no story id: {result!r}")


def _target_value(result):
    for key in ("target", "target_count", "count"):
        if key in result:
            return result[key]
    raise AssertionError(f"result has no target: {result!r}")


def test_mints_waiting_story_with_target(fake_bd):
    intent_id = _intent()
    result = smoke_story(intent_id, 7)
    story_id = _story_id(result)
    assert _target_value(result) == 7
    shown = record_show_item(story_id)
    assert shown["kind"] == "story"
    assert shown["state"] == "waiting"
    criteria = record_run(["show", story_id])[0]["acceptance_criteria"]
    assert "7" in criteria
    assert "pipeline_run_count" in shown["sheet"]


def test_mints_distinct_stories_for_distinct_targets(fake_bd):
    intent_id = _intent()
    first = smoke_story(intent_id, 8)
    second = smoke_story(intent_id, 9)
    assert _story_id(first) != _story_id(second)
    assert _target_value(first) == 8
    assert _target_value(second) == 9


def test_minted_story_stays_in_sheet_todo(fake_bd):
    story_id = _story_id(smoke_story(_intent(), 10))
    shown = record_show_item(story_id)
    assert shown["state"] == "waiting"
    labels = record_run(["show", story_id])[0]["labels"]
    assert "cut" not in labels
