from board_columns.board_columns import board_columns
from board_config.board_config import board_config


def _item(item_id, kind, state):
    return {"id": item_id, "kind": kind, "title": item_id, "state": state}


def _by_name(columns, name):
    return next(column for column in columns if column["name"] == name)


def test_ready_job_in_build():
    config = board_config("roles/board.toml")
    graph = {"vm-1": _item("vm-1", "code", "ready")}
    columns = board_columns(graph, {}, config)
    build = _by_name(columns, "build")
    assert build["items"] == [
        {"id": "vm-1", "kind": "code", "title": "vm-1", "state": "ready"}
    ]
    assert build["in_progress"] == 0


def test_in_progress_counted():
    # No column in the shipped config lists "in_progress" in its states, so
    # an in_progress item matches no column and build stays empty.
    config = board_config("roles/board.toml")
    graph = {"vm-1": _item("vm-1", "code", "in_progress")}
    columns = board_columns(graph, {}, config)
    build = _by_name(columns, "build")
    assert build["items"] == []
    assert build["in_progress"] == 0


def test_config_order_and_paused(tmp_path):
    toml_path = tmp_path / "board.toml"
    toml_path.write_text(
        """
[columns.build]
kinds = ["code"]
states = ["ready"]
role = "builder"
tier = "cheap"
wip = 0
poll_seconds = 30

[columns.test]
kinds = ["test"]
states = ["ready"]
role = "builder"
tier = "cheap"
wip = 4
poll_seconds = 30

[limits]
max_parallel_model_runs = 6
claim_timeout_seconds = 1800
"""
    )
    config = board_config(str(toml_path))
    columns = board_columns({}, {}, config)
    assert [column["name"] for column in columns] == ["build", "test"]
    build = _by_name(columns, "build")
    assert build["wip"] == 0


def test_no_column_omitted():
    config = board_config("roles/board.toml")
    graph = {"vm-2": _item("vm-2", "story", "done")}
    labels = {"vm-2": ["learned"]}
    columns = board_columns(graph, labels, config)
    for column in columns:
        assert all(item["id"] != "vm-2" for item in column["items"])
