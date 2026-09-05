from fake_list.fake_list import fake_list


def _db():
    items = {
        "a": {
            "id": "a",
            "status": "open",
            "issue_type": "task",
            "labels": ["kind:code"],
        },
        "b": {"id": "b", "status": "closed", "issue_type": "task", "labels": []},
        "e": {"id": "e", "status": "open", "issue_type": "event", "labels": []},
    }
    return {"items": items, "deps": [], "comments": {"a": [{"text": "x"}]}, "clock": 0}


def test_open_only_by_default():
    assert [r["id"] for r in fake_list(["list"], _db())] == ["a", "e"]


def test_all_and_type_filters():
    assert len(fake_list(["list", "--all"], _db())) == 3
    assert [
        r["id"] for r in fake_list(["list", "--all", "--type", "event"], _db())
    ] == ["e"]
    assert "e" not in [
        r["id"] for r in fake_list(["list", "--all", "--exclude-type", "event"], _db())
    ]


def test_label_and_counts():
    rows = fake_list(["list", "--all", "-l", "kind:code"], _db())
    assert [r["id"] for r in rows] == ["a"] and rows[0]["comment_count"] == 1
