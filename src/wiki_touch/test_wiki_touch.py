import pytest

from wiki_read.wiki_read import wiki_read
from wiki_touch.wiki_touch import wiki_touch
from wiki_write.wiki_write import wiki_write


def _page(page_id):
    return {
        "id": page_id,
        "title": "t",
        "pattern": "p",
        "evidence": ["e1"],
        "cost": 1,
        "fix": "f",
        "created": "2020-01-01T00:00:00",
        "last_used": "2020-01-01T00:00:00",
        "times_used": 2,
    }


def test_touch_increments(tmp_path):
    root = str(tmp_path)
    wiki_write(root, _page("a"))
    now = "2021-02-03T04:05:06"
    result = wiki_touch(root, "a", now)
    assert result["times_used"] == 3
    assert result["last_used"] == now


def test_touch_persists(tmp_path):
    root = str(tmp_path)
    wiki_write(root, _page("b"))
    now = "2022-03-04T05:06:07"
    wiki_touch(root, "b", now)
    reread = wiki_read(root, "b")
    assert reread["times_used"] == 3
    assert reread["last_used"] == now


def test_touch_missing_raises(tmp_path):
    root = str(tmp_path)
    with pytest.raises(FileNotFoundError):
        wiki_touch(root, "missing", "2020-01-01T00:00:00")
