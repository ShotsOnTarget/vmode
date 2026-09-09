import pytest

from fake_update.fake_update import fake_update


def _db():
    item = {"id": "c", "status": "open", "labels": [], "assignee": None, "parent": None}
    return {"items": {"c": item}, "deps": [], "comments": {}, "clock": 0}


def test_fields(tmp_path):
    db = _db()
    body = tmp_path / "b.md"
    body.write_text("sheet")
    args = [
        "update",
        "c",
        "-s",
        "closed",
        "--body-file",
        str(body),
        "--acceptance",
        "1. x",
    ]
    row = fake_update(args + ["--add-label", "state:done", "--parent", "p"], db, "t")[0]
    assert row["status"] == "closed" and row["description"] == "sheet"
    assert row["acceptance_criteria"] == "1. x" and row["labels"] == ["state:done"]
    assert row["parent"] == "p"


def test_remove_label_and_repeated_flags():
    """--remove-label takes a label off, and a repeated flag applies once per
    occurrence, so one update can swap a state label as bd does."""
    db = _db()
    db["items"]["c"]["labels"] = ["kind:code", "state:waiting"]
    args = ["update", "c", "--remove-label", "state:waiting"]
    args += ["--add-label", "state:ready", "--add-label", "cut", "-s", "open"]
    row = fake_update(args, db, "t")[0]
    assert row["labels"] == ["kind:code", "state:ready", "cut"]


def test_claim_and_release():
    db = _db()
    fake_update(["update", "c", "--claim", "--actor", "b-1"], db, "t")
    with pytest.raises(ValueError):
        fake_update(["update", "c", "--claim", "--actor", "b-2"], db, "t")
    assert fake_update(["update", "c", "-a", ""], db, "t")[0]["assignee"] is None
