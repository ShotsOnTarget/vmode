import pytest

from pattern_write.pattern_write import pattern_write
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _story():
    intent = record_create_item("intent", "I", "board")
    return record_create_item("story", "S", "architect", intent["id"])["id"]


def _page(cited):
    return {
        "title": "sheets guess shapes",
        "pattern": "p",
        "fix": "f",
        "cited": cited,
        "created": "2026-09-05T10:00:00Z",
    }


def test_pattern_with_two_cited(fake_bd):
    story = _story()
    a = record_create_item("code", "a code", "supervisor", story)["id"]
    b = record_create_item("code", "b code", "supervisor", story)["id"]
    pid = pattern_write(story, _page([a, b]))
    graph = record_graph()
    assert graph[pid]["kind"] == "pattern" and graph[pid]["parent"] == story
    shown = record_run(["show", pid])[0]
    assert "## Pattern" in shown["description"] and "## Fix" in shown["description"]
    assert {
        d["id"] for d in shown["dependencies"] if d["dependency_type"] == "relates-to"
    } == {a, b}
    assert "used:0" in shown["labels"] and "last_used:2026-09-05" in shown["labels"]


def test_one_cited_rejected(fake_bd):
    story = _story()
    with pytest.raises(ValueError):
        pattern_write(story, _page([story]))


def test_missing_field_rejected(fake_bd):
    with pytest.raises(ValueError):
        pattern_write(_story(), {"title": "t", "cited": ["x", "y"]})
