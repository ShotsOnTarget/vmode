import pytest

from fake_show.fake_show import fake_show


def _db():
    items = {"p": {"id": "p", "status": "open"}, "c": {"id": "c", "status": "open"}}
    deps = [{"issue_id": "c", "depends_on_id": "p", "type": "parent-child"}]
    return {
        "items": items,
        "deps": deps,
        "comments": {"c": [{"text": "hi"}]},
        "clock": 0,
    }


def test_shape():
    row = fake_show("c", _db())[0]
    assert row["dependencies"][0]["id"] == "p"
    assert row["dependencies"][0]["dependency_type"] == "parent-child"
    assert row["comments"] == [{"text": "hi"}]


def test_dependents():
    assert fake_show("p", _db())[0]["dependents"][0]["id"] == "c"


def test_unknown_raises():
    with pytest.raises(LookupError):
        fake_show("zz", _db())
