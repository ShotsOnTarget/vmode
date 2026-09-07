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


def test_success_sets_checking(fake_bd):
    item_id = _make_item()
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _ok_invoke}

    result = claim_and_run(item, "build", "builder", options)

    assert result is True
    row = _show(item_id)
    assert "state:checking" in row["labels"]
    comments = row.get("comments", [])
    assert comments and comments[-1]["text"].startswith("usage:")


def test_lost_claim_returns_false(fake_bd):
    item_id = _make_item()
    item = _item_dict(item_id)
    record_run(["update", item_id, "--claim", "--actor", "other"])
    options = {"config": _config(), "invoke": _ok_invoke}

    result = claim_and_run(item, "build", "builder", options)

    assert result is False
    row = _show(item_id)
    assert row.get("assignee") == "other"
    assert not row.get("comments")


def test_failure_releases(fake_bd):
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


def test_label_column_adds_label(fake_bd):
    item_id = _make_item("kind:story,state:done")
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _ok_invoke}

    result = claim_and_run(item, "learn", "analyst", options)

    assert result is True
    row = _show(item_id)
    assert "learned" in row["labels"]
    assert "state:done" in row["labels"]
    assert not row.get("assignee")


def test_claim_line_names_the_item(fake_bd, capsys):
    item_id = _make_item()
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _ok_invoke}

    claim_and_run(item, "build", "builder", options)

    lines = capsys.readouterr().out.splitlines()
    claim_lines = [line for line in lines if line.startswith("claim")]
    assert len(claim_lines) == 1
    assert item_id in claim_lines[0]
    assert "build" in claim_lines[0]


def test_finish_line_names_the_item(fake_bd, capsys):
    item_id = _make_item()
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _ok_invoke}

    claim_and_run(item, "build", "builder", options)

    lines = capsys.readouterr().out.splitlines()
    claim_index = next(i for i, line in enumerate(lines) if line.startswith("claim"))
    finish_index = next(i for i, line in enumerate(lines) if line.startswith("finish"))
    assert item_id in lines[finish_index]
    assert claim_index < finish_index


def test_failed_run_still_prints_finish(fake_bd, capsys):
    item_id = _make_item()
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _raising_invoke}

    claim_and_run(item, "build", "builder", options)

    lines = capsys.readouterr().out.splitlines()
    finish_lines = [line for line in lines if line.startswith("finish")]
    assert len(finish_lines) == 1
    assert item_id in finish_lines[0]


def test_lost_claim_prints_nothing(fake_bd, capsys):
    item_id = _make_item()
    item = _item_dict(item_id)
    record_run(["update", item_id, "--claim", "--actor", "other"])
    options = {"config": _config(), "invoke": _ok_invoke}

    claim_and_run(item, "build", "builder", options)

    assert capsys.readouterr().out == ""


def test_label_column_keeps_role_state(fake_bd):
    from record_set_state.record_set_state import record_set_state

    item_id = record_run(
        [
            "create",
            "N",
            "-t",
            "task",
            "-l",
            "kind:note,state:waiting",
            "--no-inherit-labels",
        ]
    )["id"]
    config = _config()
    item = record_graph()[item_id]

    def dispose(item, column):
        record_set_state(item["id"], "done")
        return {"tokens": 1, "seconds": 0.1}

    assert claim_and_run(
        item, "triage", "analyst", {"config": config, "invoke": dispose}
    )
    shown = record_run(["show", item_id])[0]
    assert "state:done" in shown["labels"] and "triaged" in shown["labels"]
