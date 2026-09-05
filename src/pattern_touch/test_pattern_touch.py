import pytest

from pattern_read.pattern_read import pattern_read
from pattern_touch.pattern_touch import pattern_touch
from pattern_write.pattern_write import pattern_write
from record_create_item.record_create_item import record_create_item


def _pattern():
    intent = record_create_item("intent", "I", "board")
    story = record_create_item("story", "S", "architect", intent["id"])["id"]
    a = record_create_item("code", "a code", "supervisor", story)["id"]
    b = record_create_item("code", "b code", "supervisor", story)["id"]
    page = {
        "title": "t",
        "pattern": "p",
        "fix": "f",
        "cited": [a, b],
        "created": "2026-09-01",
    }
    return pattern_write(story, page)


def test_touch_increments(fake_bd):
    pid = _pattern()
    assert pattern_touch(pid, "2026-09-05") == {
        "id": pid,
        "used": 1,
        "last_used": "2026-09-05",
    }
    pattern_touch(pid, "2026-09-06")
    got = pattern_read(pid)
    assert got["used"] == 2 and got["last_used"] == "2026-09-06"


def test_not_pattern_raises(fake_bd):
    intent = record_create_item("intent", "I", "board")["id"]
    with pytest.raises(ValueError):
        pattern_touch(intent, "2026-09-05")
