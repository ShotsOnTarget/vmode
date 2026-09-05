import pytest

from ready_check.ready_check import ready_check


def _g(*items):
    return {i["id"]: i for i in items}


def _job(i, title, state, kind="code"):
    return {"id": i, "kind": kind, "title": title, "state": state}


def test_clean_pair_passes():
    graph = _g(_job("c", "w code", "waiting"), _job("t", "w test", "done", "test"))
    assert ready_check("c", graph) == []


def test_duplicate_function_refused():
    graph = _g(_job("c", "w code", "waiting"), _job("d", "w code", "done"))
    assert ready_check("c", graph) == ["duplicate_function"]


def test_folder_conflict_refused():
    graph = _g(
        _job("c", "w code", "waiting"), _job("t", "w test", "in_progress", "test")
    )
    assert ready_check("c", graph) == ["folder_conflict"]


def test_other_kinds_pass():
    graph = _g({"id": "s", "kind": "story", "title": "S", "state": "waiting"})
    assert ready_check("s", graph) == []


def test_unknown_raises():
    with pytest.raises(ValueError):
        ready_check("nope", {})
