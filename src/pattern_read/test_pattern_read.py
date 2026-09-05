import pytest

from pattern_read.pattern_read import pattern_read
from pattern_write.pattern_write import pattern_write
from record_create_item.record_create_item import record_create_item


def _story():
    intent = record_create_item("intent", "I", "board")
    return record_create_item("story", "S", "architect", intent["id"])["id"]


def test_reads_back(fake_bd):
    story = _story()
    a = record_create_item("code", "a code", "supervisor", story)["id"]
    b = record_create_item("code", "b code", "supervisor", story)["id"]
    page = {
        "title": "t",
        "pattern": "what happens",
        "fix": "change X",
        "cited": [a, b],
        "cost": 12,
        "created": "2026-09-05",
    }
    pid = pattern_write(story, page)
    got = pattern_read(pid)
    assert got["pattern"] == "what happens" and got["fix"] == "change X"
    assert got["cost"] == 12 and set(got["cited"]) == {a, b}
    assert got["used"] == 0 and got["last_used"] == "2026-09-05"


def test_not_pattern_raises(fake_bd):
    with pytest.raises(ValueError):
        pattern_read(_story())
