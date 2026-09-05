import pytest

from create_pair.create_pair import create_pair
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph


def _story():
    intent = record_create_item("intent", "I", "board")
    return record_create_item("story", "S", "architect", intent["id"])["id"]


def test_siblings_under_story(fake_bd):
    story = _story()
    pair = create_pair(story, "widget", "supervisor")
    graph = record_graph()
    assert graph[pair["code"]]["parent"] == story
    assert graph[pair["test"]]["parent"] == story


def test_code_needs_test(fake_bd):
    story = _story()
    pair = create_pair(story, "widget", "supervisor")
    graph = record_graph()
    assert graph[pair["code"]]["needs"] == [pair["test"]]
    assert graph[pair["test"]]["checks"] == [pair["code"]]


def test_bad_name_rejected(fake_bd):
    with pytest.raises(ValueError):
        create_pair(_story(), "two words", "supervisor")
