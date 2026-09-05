import pytest

from fake_links.fake_links import fake_links


def _db():
    items = {
        "p": {"id": "p", "labels": [], "parent": None},
        "c": {"id": "c", "labels": ["x"], "parent": "p"},
        "d": {"id": "d", "labels": [], "parent": "p"},
    }
    return {
        "items": items,
        "deps": [{"issue_id": "c", "depends_on_id": "p", "type": "parent-child"}],
        "comments": {},
        "clock": 0,
    }


def test_label_round_trip():
    db = _db()
    fake_links(["label", "add", "c", "y"], db, "t")
    assert fake_links(["label", "list", "c"], db, "t") == ["x", "y"]
    fake_links(["label", "remove", "c", "x"], db, "t")
    assert fake_links(["label", "list", "c"], db, "t") == ["y"]


def test_dep_child_to_parent_refused():
    db = _db()
    with pytest.raises(ValueError):
        fake_links(["dep", "add", "c", "p", "-t", "validates"], db, "t")
    assert (
        fake_links(["dep", "add", "c", "--blocked-by", "d"], db, "t")["type"]
        == "blocks"
    )


def test_comment():
    db = _db()
    row = fake_links(["comment", "c", "hi"], db, "t")
    assert row["text"] == "hi" and db["comments"]["c"] == [row]
