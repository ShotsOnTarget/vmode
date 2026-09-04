import pytest

from wip_headroom.wip_headroom import wip_headroom


def test_full_is_zero():
    graph = {
        "a": {"kind": "code", "state": "in_progress"},
        "b": {"kind": "code", "state": "in_progress"},
    }
    config = {"columns": {"build": {"wip": 2, "kinds": ["code"]}}}
    assert wip_headroom("build", graph, config) == 0


def test_never_negative():
    graph = {
        "a": {"kind": "code", "state": "in_progress"},
        "b": {"kind": "code", "state": "in_progress"},
        "c": {"kind": "code", "state": "in_progress"},
    }
    config = {"columns": {"build": {"wip": 1, "kinds": ["code"]}}}
    assert wip_headroom("build", graph, config) == 0


def test_counts_only_column_kinds():
    graph = {
        "a": {"kind": "code", "state": "in_progress"},
        "b": {"kind": "story", "state": "in_progress"},
    }
    config = {"columns": {"build": {"wip": 2, "kinds": ["code"]}}}
    assert wip_headroom("build", graph, config) == 1


def test_unknown_column_raises():
    graph = {}
    config = {"columns": {"build": {"wip": 2, "kinds": ["code"]}}}
    with pytest.raises(ValueError):
        wip_headroom("nope", graph, config)
