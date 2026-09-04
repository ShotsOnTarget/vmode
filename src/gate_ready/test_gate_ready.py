import pytest

from gate_ready.gate_ready import gate_ready


def test_code_without_test():
    graph = {
        "intent1": {"kind": "intent", "parent": None, "checks": []},
        "story1": {"kind": "story", "parent": "intent1", "checks": []},
        "code1": {"kind": "code", "parent": "story1", "checks": []},
    }
    sheets = {}

    result = gate_ready("story1", graph, sheets)

    assert "code_without_test" in result


def test_no_intent():
    graph = {
        "story1": {"kind": "story", "parent": None, "checks": []},
    }
    sheets = {}

    result = gate_ready("story1", graph, sheets)

    assert "no_intent" in result


def test_sheet_missing():
    graph = {
        "intent1": {"kind": "intent", "parent": None, "checks": []},
        "story1": {"kind": "story", "parent": "intent1", "checks": []},
        "code1": {"kind": "code", "parent": "story1", "checks": []},
        "test1": {"kind": "test", "parent": "story1", "checks": ["code1"]},
        "verif1": {"kind": "verification", "parent": "story1", "checks": ["story1"]},
        "valid1": {"kind": "validation", "parent": "intent1", "checks": ["intent1"]},
    }
    sheets = {"code1": "sheet text"}

    result = gate_ready("story1", graph, sheets)

    assert "sheet_missing" in result


def test_clean_passes():
    graph = {
        "intent1": {"kind": "intent", "parent": None, "checks": []},
        "story1": {"kind": "story", "parent": "intent1", "checks": []},
        "code1": {"kind": "code", "parent": "story1", "checks": []},
        "test1": {"kind": "test", "parent": "story1", "checks": ["code1"]},
        "verif1": {"kind": "verification", "parent": "story1", "checks": ["story1"]},
        "valid1": {"kind": "validation", "parent": "intent1", "checks": ["intent1"]},
    }
    sheets = {"code1": "sheet text", "test1": "sheet text"}

    result = gate_ready("story1", graph, sheets)

    assert result == []


def test_not_a_story_raises():
    graph = {
        "code1": {"kind": "code", "parent": None, "checks": []},
    }
    sheets = {}

    with pytest.raises(ValueError):
        gate_ready("code1", graph, sheets)
