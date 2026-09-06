import pytest
from cutter_gather.cutter_gather import cutter_gather

from log_append.log_append import log_append
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph


def _intent():
    return record_create_item("intent", "intent1", "supervisor")["id"]


def _story(intent_id, title="story1"):
    return record_create_item("story", title, "supervisor", parent=intent_id)["id"]


def _job(story_id, title="job1"):
    return record_create_item("code", title, "supervisor", parent=story_id)["id"]


def _ready(item_id, tokens=0, usd=None, inputs=None):
    log_append(
        {
            "item": item_id,
            "gate": "ready",
            "rule": "r",
            "inputs": {} if inputs is None else inputs,
            "state": "s",
            "tokens": tokens,
            "seconds": 0,
            "usd": usd,
            "actor": "supervisor",
        }
    )


def _built(item_id, action):
    log_append(
        {
            "item": item_id,
            "gate": "built",
            "rule": "r",
            "inputs": {"action": action},
            "state": "s",
            "tokens": 0,
            "seconds": 0,
            "actor": "supervisor",
        }
    )


def _proven(item_id, action):
    log_append(
        {
            "item": item_id,
            "gate": "proven",
            "rule": "r",
            "inputs": {"action": action},
            "state": "s",
            "tokens": 0,
            "seconds": 0,
            "actor": "supervisor",
        }
    )


def test_one_story_with_a_ready_event_gives_one_dict(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story)

    result = cutter_gather(intent, record_graph())

    assert len(result) == 1
    assert result[0]["story"] == story


def test_setting_joins_harness_model_and_effort(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(
        story, inputs={"harness": "claude_code", "model": "fable", "effort": "medium"}
    )

    result = cutter_gather(intent, record_graph())

    assert result[0]["setting"] == "claude_code/fable/medium"


def test_absent_setting_values_are_written_none(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, inputs={})

    result = cutter_gather(intent, record_graph())

    assert result[0]["setting"] == "none/none/none"


def test_null_effort_is_written_none(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, inputs={"harness": "claude_code", "model": "fable", "effort": None})

    result = cutter_gather(intent, record_graph())

    assert result[0]["setting"] == "claude_code/fable/none"


def test_pairs_come_from_the_latest_ready_event(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, inputs={"pairs": 2})
    _ready(story, inputs={"pairs": 6})

    result = cutter_gather(intent, record_graph())

    assert result[0]["pairs"] == 6


def test_absent_pairs_gives_zero(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, inputs={})

    result = cutter_gather(intent, record_graph())

    assert result[0]["pairs"] == 0


def test_tokens_sum_over_every_ready_event(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, tokens=100)
    _ready(story, tokens=250)

    result = cutter_gather(intent, record_graph())

    assert result[0]["tokens"] == 350


def test_negative_tokens_count_as_zero(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, tokens=-1)

    result = cutter_gather(intent, record_graph())

    assert result[0]["tokens"] == 0


def test_usd_sums_and_none_counts_as_zero(fake_bd):
    intent = _intent()
    story = _story(intent)
    _ready(story, usd=1.5)
    _ready(story, usd=None)

    result = cutter_gather(intent, record_graph())

    assert result[0]["usd"] == 1.5


def test_bounces_count_built_events_under_the_story(fake_bd):
    intent = _intent()
    story = _story(intent)
    job = _job(story)
    _ready(story)
    _built(job, "bounce")
    _built(job, "bounce")
    _built(job, "log_done")

    result = cutter_gather(intent, record_graph())

    assert result[0]["bounces"] == 2


def test_escalate_counts_as_a_bounce(fake_bd):
    intent = _intent()
    story = _story(intent)
    job = _job(story)
    _ready(story)
    _built(job, "escalate")

    result = cutter_gather(intent, record_graph())

    assert result[0]["bounces"] == 1


def test_proven_events_are_not_counted(fake_bd):
    intent = _intent()
    story = _story(intent)
    job = _job(story)
    _ready(story)
    _built(job, "bounce")
    _proven(job, "bounce")

    result = cutter_gather(intent, record_graph())

    assert result[0]["bounces"] == 1


def test_blocked_counts_supervisor_notes_under_the_story(fake_bd):
    intent = _intent()
    story = _story(intent)
    job = _job(story)
    _ready(story)
    record_create_item("note", "n1", "supervisor", parent=job)
    record_create_item("note", "n2", "supervisor", parent=job)

    result = cutter_gather(intent, record_graph())

    assert result[0]["blocked"] == 2


def test_a_note_owned_by_another_role_is_not_blocked(fake_bd):
    intent = _intent()
    story = _story(intent)
    job = _job(story)
    _ready(story)
    record_create_item("note", "n1", "supervisor", parent=job)
    record_create_item("note", "n2", "analyst", parent=job)

    result = cutter_gather(intent, record_graph())

    assert result[0]["blocked"] == 1


def test_a_story_without_a_ready_event_is_absent(fake_bd):
    intent = _intent()
    story = _story(intent)
    _built(story, "log_done")

    result = cutter_gather(intent, record_graph())

    assert result == []


def test_a_ready_event_on_a_job_is_not_a_cut(fake_bd):
    intent = _intent()
    story = _story(intent)
    job = _job(story)
    _ready(job)

    result = cutter_gather(intent, record_graph())

    assert result == []


def test_two_stories_are_sorted_by_story_id(fake_bd):
    intent = _intent()
    story_a = _story(intent, "story-a")
    story_b = _story(intent, "story-b")
    _ready(story_b)
    _ready(story_a)

    result = cutter_gather(intent, record_graph())

    assert [r["story"] for r in result] == sorted([story_a, story_b])


def test_unknown_item_id_raises(fake_bd):
    with pytest.raises(ValueError):
        cutter_gather("nope", record_graph())
