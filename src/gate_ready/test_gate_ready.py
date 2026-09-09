import pytest

from gate_ready.gate_ready import gate_ready


def _node(kind, parent, checks=None):
    return {"kind": kind, "parent": parent, "checks": list(checks) if checks else []}


def _code(function="f", change=None):
    lines = [
        "# Instruction sheet",
        "",
        "- **Job id**: c1",
        "- **Kind**: code",
    ]
    if change is not None:
        lines.append(f"- **Change**: {change}")
    lines.extend(
        [
            "- **Parent Story**: s",
            f"- **Function name**: `{function}`",
            f"- **Folder**: `src/{function}/`",
            "- **Signature**: `f() -> None`",
            "- **Inputs**: x: a value.",
            "- **Outputs**: Return an empty list.",
            "- **Checklist items this job serves**: 1",
        ]
    )
    return "\n".join(lines) + "\n"


def _test_sheet(function="f", cases=None, removed=None):
    if cases is None:
        cases = ["test_first", "test_second"]
    if removed is None:
        removed = []
    lines = [
        "# Instruction sheet",
        "",
        "- **Job id**: t1",
        "- **Kind**: test",
        "- **Parent Story**: s",
        f"- **Function name**: `{function}`",
        f"- **Folder**: `src/{function}/`",
        "- **Signature**: `f() -> None`",
        "- **Inputs**: x: a value.",
        "- **Outputs**: Return an empty list.",
        "- **Checklist items this job serves**: 1",
        "- **Cases**:",
    ]
    for name in cases:
        lines.append(f"  - `{name}`: works")
    for name in removed:
        lines.append(f"  - `{name}`: removed, superseded")
    return "\n".join(lines) + "\n"


def _extras(checklist=None, existing=None):
    if checklist is None:
        checklist = ["Do x [testing]"]
    if existing is None:
        existing = []
    return {"checklist": list(checklist), "existing": existing}


def _clean_graph():
    graph = {
        "intent1": _node("intent", None),
        "story1": _node("story", "intent1"),
        "code1": _node("code", "story1"),
        "test1": _node("test", "story1", ["code1"]),
        "verif1": _node("verification", "story1", ["story1"]),
        "valid1": _node("validation", "intent1", ["intent1"]),
    }
    sheets = {"code1": _code("f"), "test1": _test_sheet("f")}
    return graph, sheets


def test_code_without_test():
    graph = {
        "intent1": _node("intent", None),
        "story1": _node("story", "intent1"),
        "code1": _node("code", "story1"),
        "verif1": _node("verification", "story1", ["story1"]),
        "valid1": _node("validation", "intent1", ["intent1"]),
    }
    sheets = {"code1": _code("f")}
    result = gate_ready("story1", graph, sheets, _extras())
    assert "code_without_test" in result


def test_no_intent():
    graph = {"story1": _node("story", None)}
    result = gate_ready("story1", graph, {}, _extras())
    assert "no_intent" in result


def test_sheet_missing():
    graph, sheets = _clean_graph()
    sheets = {"code1": sheets["code1"]}
    result = gate_ready("story1", graph, sheets, _extras())
    assert "sheet_missing" in result


def test_clean_passes():
    graph, sheets = _clean_graph()
    assert gate_ready("story1", graph, sheets, _extras()) == []


def test_not_a_story_raises():
    graph, sheets = _clean_graph()
    with pytest.raises(ValueError):
        gate_ready("code1", graph, sheets, _extras())
    with pytest.raises(ValueError):
        gate_ready("missing", graph, sheets, _extras())


def test_no_checklist():
    graph, sheets = _clean_graph()
    result = gate_ready("story1", graph, sheets, _extras(checklist=[]))
    assert "no_checklist" in result


def test_checklist_method():
    graph, sheets = _clean_graph()
    result = gate_ready("story1", graph, sheets, _extras(checklist=["works fine"]))
    assert "checklist_method" in result


def test_sheet_rules_prefixed():
    graph, sheets = _clean_graph()
    sheets["test1"] = _test_sheet("f", cases=[])
    result = gate_ready("story1", graph, sheets, _extras())
    assert "sheet_no_cases" in result


def test_sheet_rules_skipped_when_sheet_missing():
    graph, sheets = _clean_graph()
    del sheets["test1"]
    result = gate_ready("story1", graph, sheets, _extras())
    assert result == ["sheet_missing"]
    assert "sheet_no_cases" not in result


def test_order_and_no_repeats():
    graph = {
        "mid": _node("story", None),
        "story1": _node("story", "mid"),
        "code1": _node("code", "story1"),
        "code2": _node("code", "story1"),
        "test1": _node("test", "story1", ["code1"]),
        "test2": _node("test", "story1", ["code2"]),
        "verif1": _node("verification", "story1", ["story1"]),
    }
    sheets = {
        "code1": _code("f"),
        "code2": _code("f"),
        "test1": _test_sheet("f", cases=[]),
        "test2": _test_sheet("f", cases=[]),
    }
    extras = _extras(checklist=["works fine", "Do y [looking]"])
    assert gate_ready("story1", graph, sheets, extras) == [
        "no_intent",
        "checklist_method",
        "sheet_no_cases",
    ]


def test_extras_none_graph_rules_only():
    graph, sheets = _clean_graph()
    sheets["test1"] = _test_sheet("f", cases=[])
    result = gate_ready("story1", graph, sheets)
    assert result == []
    assert "no_checklist" not in result
    assert "sheet_no_cases" not in result


def test_existing_case_missing():
    graph, sheets = _clean_graph()
    sheets["code1"] = _code("f", change="reworked the outputs")
    sheets["test1"] = _test_sheet("f", cases=["test_first"])
    extras = _extras(existing={"f": ["test_first", "test_dropped"]})
    result = gate_ready("story1", graph, sheets, extras)
    assert "sheet_existing_case_missing:test_dropped" in result


def test_existing_case_kept_passes():
    graph, sheets = _clean_graph()
    sheets["code1"] = _code("f", change="reworked the outputs")
    sheets["test1"] = _test_sheet("f", cases=["test_first", "test_second"])
    extras = _extras(existing={"f": ["test_first", "test_second"]})
    assert gate_ready("story1", graph, sheets, extras) == []


def test_existing_case_removed_passes():
    graph, sheets = _clean_graph()
    sheets["code1"] = _code("f", change="reworked the outputs")
    sheets["test1"] = _test_sheet("f", cases=["test_first"], removed=["test_second"])
    extras = _extras(existing={"f": ["test_first", "test_second"]})
    assert gate_ready("story1", graph, sheets, extras) == []
