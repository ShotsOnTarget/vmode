from datetime import UTC, datetime, timedelta

import pytest
from open_questions.open_questions import open_questions


def _iso(when):
    return when.strftime("%Y-%m-%dT%H:%M:%SZ")


def _item(item_id, kind, parent, title):
    return {"id": item_id, "kind": kind, "title": title, "parent": parent}


def _graph():
    return {
        "vm-intent": _item("vm-intent", "intent", None, "An intent"),
        "vm-story": _item("vm-story", "story", "vm-intent", "A story"),
        "vm-job": _item("vm-job", "code", "vm-story", "A job"),
    }


def _note(note_id, title, owner, parent, created, comments=(), state="open"):
    return {
        "id": note_id,
        "kind": "note",
        "title": title,
        "owner": owner,
        "parent": parent,
        "created_at": _iso(created),
        "comments": [{"text": text} for text in comments],
        "state": state,
    }


NOW = datetime(2026, 9, 7, 12, 0, 0, tzinfo=UTC)


def test_returns_old_unanswered_questions_and_age():
    notes = [
        _note("vm-1", "old question", "engineer", "vm-job", NOW - timedelta(hours=50)),
        _note(
            "vm-2",
            "owner answered",
            "engineer",
            "vm-job",
            NOW - timedelta(hours=40),
            comments=("answer (engineer): fixed",),
            state="done",
        ),
        _note(
            "vm-3",
            "board answered",
            "builder",
            "vm-job",
            NOW - timedelta(hours=45),
            comments=("answer (board): agreed",),
        ),
        _note(
            "vm-4",
            "done but unanswered",
            "architect",
            "vm-job",
            NOW - timedelta(hours=30),
            comments=("looks fine",),
            state="done",
        ),
        _note(
            "vm-5",
            "young question",
            "engineer",
            "vm-job",
            NOW - timedelta(hours=10),
        ),
    ]

    result = open_questions(notes, _graph(), 24.0, NOW)

    assert [q["id"] for q in result] == ["vm-1", "vm-4"]
    assert result[0]["title"] == "old question"
    assert result[0]["owner"] == "engineer"
    assert result[0]["story"] == "vm-story"
    assert result[0]["age_hours"] == pytest.approx(50.0)
    assert result[1]["title"] == "done but unanswered"
    assert result[1]["owner"] == "architect"
    assert result[1]["story"] == "vm-story"
    assert result[1]["age_hours"] == pytest.approx(30.0)
    assert set(result[0]) == {"id", "title", "owner", "story", "age_hours"}


def test_excludes_disposition_owners_and_zero_hours_returns_all():
    notes = [
        _note("vm-a", "analyst note", "analyst", "vm-job", NOW - timedelta(hours=100)),
        _note(
            "vm-s",
            "supervisor note",
            "supervisor",
            "vm-job",
            NOW - timedelta(hours=90),
        ),
        _note("vm-e", "engineer note", "engineer", "vm-job", NOW - timedelta(hours=26)),
        _note("vm-b", "builder note", "builder", "vm-job", NOW - timedelta(hours=3)),
        _note(
            "vm-f",
            "fresh note",
            "engineer",
            "vm-job",
            NOW - timedelta(minutes=30),
        ),
        _note(
            "vm-x",
            "answered note",
            "engineer",
            "vm-job",
            NOW - timedelta(hours=40),
            comments=("answer (board): fine",),
        ),
    ]

    result = open_questions(notes, _graph(), 0.0, NOW)

    assert [q["id"] for q in result] == ["vm-e", "vm-b", "vm-f"]
    assert [q["story"] for q in result] == ["vm-story", "vm-story", "vm-story"]


def test_resolves_story_for_job_story_and_intent_parents():
    notes = [
        _note("vm-j", "job note", "engineer", "vm-job", NOW - timedelta(hours=6)),
        _note("vm-st", "story note", "engineer", "vm-story", NOW - timedelta(hours=5)),
        _note(
            "vm-it",
            "intent note",
            "engineer",
            "vm-intent",
            NOW - timedelta(hours=4),
        ),
    ]

    result = open_questions(notes, _graph(), 0.0, NOW)

    assert [q["id"] for q in result] == ["vm-j", "vm-st", "vm-it"]
    assert result[0]["story"] == "vm-story"
    assert result[1]["story"] == "vm-story"
    assert result[2]["story"] == "vm-intent"
    assert result[0]["age_hours"] == pytest.approx(6.0)
    assert result[1]["age_hours"] == pytest.approx(5.0)
    assert result[2]["age_hours"] == pytest.approx(4.0)
