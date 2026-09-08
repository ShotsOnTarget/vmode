import pathlib

from board_config.board_config import board_config
from claim_and_run.claim_and_run import claim_and_run
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state

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
    assert "boom" in comments[-1]["text"]


def test_failure_releases_prior_state(fake_bd):
    item_id = _make_item("kind:note,state:waiting")
    item = _item_dict(item_id)
    options = {"config": _config(), "invoke": _raising_invoke}

    result = claim_and_run(item, "triage", "analyst", options)

    assert result is True
    row = _show(item_id)
    assert "state:waiting" in row["labels"]
    assert not row.get("assignee")
    comments = row.get("comments", [])
    assert comments and "boom" in comments[-1]["text"]


def test_done_story_failure_preserves_verification(fake_bd):
    story_id = _make_item("kind:story,state:done")
    record_run(["update", story_id, "--acceptance", "1. it works [testing]"])
    verification_id = _make_item("kind:verification,state:checking")
    record_run(["dep", "add", verification_id, story_id, "-t", "validates"])
    story = _item_dict(story_id)
    options = {"config": _config(), "invoke": _raising_invoke}

    result = claim_and_run(story, "learn", "analyst", options)

    assert result is True
    story_row = _show(story_id)
    assert "state:done" in story_row["labels"]
    assert not story_row.get("assignee")
    comments = story_row.get("comments", [])
    assert comments and "boom" in comments[-1]["text"]
    verification_row = _show(verification_id)
    assert "state:checking" in verification_row["labels"]


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


def test_label_column_keeps_role_state(fake_bd):
    item_id = _make_item("kind:note,state:waiting")
    item = _item_dict(item_id)
    config = _config()

    def dispose(current, column):
        record_set_state(current["id"], "done")
        return {"tokens": 1, "seconds": 0.1}

    assert claim_and_run(
        item, "triage", "analyst", {"config": config, "invoke": dispose}
    )
    shown = _show(item_id)
    assert "state:done" in shown["labels"]
    assert "triaged" in shown["labels"]


def test_third_failure_in_a_row_blocks_the_item(fake_bd):
    item_id = _make_item()
    options = {"config": _config(), "invoke": _raising_invoke}
    for _ in range(3):
        claim_and_run(_item_dict(item_id), "build", "builder", options)
    row = _show(item_id)
    assert "state:blocked" in row["labels"]
    assert not row.get("assignee")


def test_the_release_note_keeps_the_whole_reason(fake_bd):
    item_id = _make_item()

    def long_error(item, column):
        raise RuntimeError("timed out; " + "x" * 600)

    claim_and_run(
        _item_dict(item_id),
        "build",
        "builder",
        {"config": _config(), "invoke": long_error},
    )
    text = _show(item_id)["comments"][-1]["text"]
    assert text.startswith("release: timed out; ")
    assert len(text) > 300


def test_invoke_is_told_what_the_last_gate_said(fake_bd):
    item_id = _make_item()
    record_run(["comment", item_id, "bounce: case_missing"])
    seen = {}

    def spy(item, column):
        seen.update(item)
        return {"tokens": 1}

    claim_and_run(
        _item_dict(item_id), "build", "builder", {"config": _config(), "invoke": spy}
    )
    assert seen["last_gate"] == "bounce: case_missing"


def test_invoke_gets_an_empty_last_gate_on_a_fresh_item(fake_bd):
    item_id = _make_item()
    seen = {}

    def spy(item, column):
        seen.update(item)
        return {"tokens": 1}

    claim_and_run(
        _item_dict(item_id), "build", "builder", {"config": _config(), "invoke": spy}
    )
    assert seen["last_gate"] == ""


def test_a_long_report_is_trimmed_in_the_usage_note(fake_bd):
    item_id = _make_item()

    def talkative(item, column):
        return {"tokens": 1, "report": "x" * 40000}

    claim_and_run(
        _item_dict(item_id),
        "build",
        "builder",
        {"config": _config(), "invoke": talkative},
    )
    text = _show(item_id)["comments"][-1]["text"]
    assert text.startswith("usage:")
    assert len(text) < 6000
    assert "trimmed" in text
