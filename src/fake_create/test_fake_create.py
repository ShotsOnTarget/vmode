from fake_create.fake_create import fake_create


def _db():
    return {"items": {}, "deps": [], "comments": {}, "clock": 0}


def test_top_and_child_ids():
    db = _db()
    top = fake_create(["create", "I", "-t", "epic"], db, "t1")
    child = fake_create(["create", "S", "--parent", top["id"], "-l", "a,b"], db, "t2")
    assert top["id"] == "vm-001" and child["id"] == "vm-001.1"
    assert db["items"][child["id"]]["labels"] == ["a", "b"]
    assert db["deps"][0]["type"] == "parent-child"


def test_title_skips_flag_values():
    db = _db()
    row = fake_create(
        ["create", "-l", "kind:code", "--no-inherit-labels", "Item"], db, "t"
    )
    assert row["title"] == "Item"


def test_event_fields():
    db = _db()
    args = [
        "create",
        "Built",
        "--type",
        "event",
        "--event-actor",
        "s",
        "--event-category",
        "built",
    ]
    row = fake_create(args + ["--event-target", "x", "--event-payload", "{}"], db, "t")
    assert (
        row["issue_type"] == "event"
        and row["event_kind"] == "built"
        and row["target"] == "x"
    )
