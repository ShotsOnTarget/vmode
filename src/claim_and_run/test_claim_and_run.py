import pathlib

from board_config.board_config import board_config
from claim_and_run.claim_and_run import claim_and_run
from record_graph.record_graph import record_graph
from record_run.record_run import record_run

_BOARD_TOML = pathlib.Path(__file__).resolve().parents[2] / "roles" / "board.toml"


def _make_item(labels="kind:code,state:ready"):
    created = record_run(["create", "-l", labels, "--no-inherit-labels", "Item"])
    item = created[0] if isinstance(created, list) else created
    return item["id"]


def _item_dict(item_id):
    return record_graph()[item_id]


def _show(item_id):
    shown = record_run(["show", item_id])
    return shown[0] if isinstance(shown, list) else shown


def _config():
    return board_config(str(_BOARD_TOML))


def _ok_invoke(item, column):
    return {"tokens": 1}


def _raising_invoke(item, column):
    raise RuntimeError("boom")


def test_success_sets_checking(bd_repo):
    item_id = _make_item()
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _ok_invoke}

    result = claim_and_run(item, "build", "builder", options)

    assert result is True
    row = _show(item_id)
    assert "state:checking" in row["labels"]
    comments = row.get("comments", [])
    assert comments and comments[-1]["text"].startswith("usage:")


def test_lost_claim_returns_false(bd_repo):
    item_id = _make_item()
    item = _item_dict(item_id)
    record_run(["update", item_id, "--claim", "--actor", "other"])
    options = {"config": _config(), "invoke": _ok_invoke}

    result = claim_and_run(item, "build", "builder", options)

    assert result is False
    row = _show(item_id)
    assert row.get("assignee") == "other"
    assert not row.get("comments")


def test_failure_releases(bd_repo):
    item_id = _make_item()
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _raising_invoke}

    result = claim_and_run(item, "build", "builder", options)

    assert result is True
    row = _show(item_id)
    assert "state:ready" in row["labels"]
    assert not row.get("assignee")
    comments = row.get("comments", [])
    assert comments and comments[-1]["text"].startswith("release:")


def test_label_column_adds_label(bd_repo):
    item_id = _make_item("kind:story,state:done")
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _ok_invoke}

    result = claim_and_run(item, "learn", "analyst", options)

    assert result is True
    row = _show(item_id)
    assert "learned" in row["labels"]
    assert "state:done" in row["labels"]
    assert not row.get("assignee")
