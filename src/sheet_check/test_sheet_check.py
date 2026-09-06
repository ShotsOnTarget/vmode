from sheet_check.sheet_check import sheet_check


def _code(function="f", folder=None, outputs="Return an empty list.", extra=""):
    fld = folder if folder is not None else f"src/{function}/"
    lines = [
        "# Instruction sheet",
        "",
        "- **Job id**: c1",
        "- **Kind**: code",
        "- **Parent Story**: s",
        f"- **Function name**: `{function}`",
        f"- **Folder**: `{fld}`",
        "- **Signature**: `f() -> None`",
        "- **Inputs**: x: a value.",
        f"- **Outputs**: {outputs}",
        "- **Checklist items this job serves**: 1",
    ]
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def _test(function="f", folder=None, cases=None, extra=""):
    fld = folder if folder is not None else f"src/{function}/"
    if cases is None:
        cases = ["test_first", "test_second"]
    lines = [
        "# Instruction sheet",
        "",
        "- **Job id**: t1",
        "- **Kind**: test",
        "- **Parent Story**: s",
        f"- **Function name**: `{function}`",
        f"- **Folder**: `{fld}`",
        "- **Signature**: `f() -> None`",
        "- **Inputs**: x: a value.",
        "- **Outputs**: Return an empty list.",
        "- **Checklist items this job serves**: 1",
        "- **Cases**:",
    ]
    for name in cases:
        lines.append(f"  - `{name}`: works")
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def test_clean_pair_empty():
    code = _code("f")
    test = _test("f")
    assert sheet_check(code, test, []) == []


def test_function_mismatch():
    code = _code("f")
    test = _test("g")
    assert "function_mismatch" in sheet_check(code, test, [])


def test_folder_mismatch():
    code = _code("f", folder="src/g/")
    test = _test("f")
    assert "folder_mismatch" in sheet_check(code, test, [])


def test_no_cases():
    code = _code("f")
    test = _test("f", cases=[])
    assert "no_cases" in sheet_check(code, test, [])


def test_forbidden_field():
    code = _code("f", extra="- **Allowed imports**: os")
    test = _test("f")
    assert "forbidden_field" in sheet_check(code, test, [])


def test_one_direction_flagged():
    code = _code("f", outputs="raise a note and clear it")
    test = _test("f", cases=["test_raise_once"])
    assert "one_direction" in sheet_check(code, test, [])


def test_one_direction_covered():
    code = _code("f", outputs="raise a note and clear it")
    test = _test("f", cases=["test_raise_once", "test_clear_stale"])
    assert "one_direction" not in sheet_check(code, test, [])


def test_validate_and_operate():
    code = _code("f", outputs="raise one raise two raise three")
    test = _test("f")
    assert "validate_and_operate" in sheet_check(code, test, [])


def test_exists_without_change():
    code = _code("f")
    test = _test("f")
    assert "exists_without_change" in sheet_check(code, test, ["f"])


def test_exists_with_change_clean():
    code = _code("f", extra="- **Change**: rewrite")
    test = _test("f")
    assert "exists_without_change" not in sheet_check(code, test, ["f"])


def test_sorted_unique():
    code = _code(
        "f",
        folder="src/g/",
        outputs="raise raise raise and clear it",
        extra="- **Allowed imports**: os",
    )
    test = _test("g", cases=[])
    result = sheet_check(code, test, ["f"])
    assert result == sorted(result)
    assert len(result) == len(set(result))
    assert len(result) >= 3
    assert "function_mismatch" in result
    assert "forbidden_field" in result
