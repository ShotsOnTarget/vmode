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


def _test(function="f", folder=None, cases=None, removed=None, extra=""):
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
    for name in removed or []:
        lines.append(f"  - `{name}`: removed, no longer needed")
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def test_clean_pair_empty():
    code = _code("f")
    test = _test("f")
    assert sheet_check(code, test, {}) == []


def test_function_mismatch():
    code = _code("f")
    test = _test("g")
    assert "function_mismatch" in sheet_check(code, test, {})


def test_folder_mismatch():
    code = _code("f", folder="src/g/")
    test = _test("f")
    assert "folder_mismatch" in sheet_check(code, test, {})


def test_no_cases():
    code = _code("f")
    test = _test("f", cases=[])
    assert "no_cases" in sheet_check(code, test, {})


def test_forbidden_field():
    code = _code("f", extra="- **Allowed imports**: os")
    test = _test("f")
    assert "forbidden_field" in sheet_check(code, test, {})


def test_one_direction_flagged():
    code = _code("f", outputs="raise a note and clear it")
    test = _test("f", cases=["test_raise_once"])
    assert "one_direction" in sheet_check(code, test, {})


def test_one_direction_covered():
    code = _code("f", outputs="raise a note and clear it")
    test = _test("f", cases=["test_raise_once", "test_clear_stale"])
    assert "one_direction" not in sheet_check(code, test, {})


def test_validate_and_operate():
    code = _code("f", outputs="raise one raise two raise three")
    test = _test("f")
    assert "validate_and_operate" in sheet_check(code, test, {})


def test_exists_without_change():
    code = _code("f")
    test = _test("f")
    existing = {"f": ["test_first", "test_second"]}
    assert "exists_without_change" in sheet_check(code, test, existing)


CHANGE = "- **Change**: rewrite\n- **Facts**: f reads x from the record (f.py)"


def test_exists_with_change_clean():
    code = _code("f", extra=CHANGE)
    test = _test("f")
    existing = {"f": ["test_first", "test_second"]}
    assert sheet_check(code, test, existing) == []


def test_change_without_facts_refused():
    """A change pair carries what the Engineer probed, or the Builders re-probe it."""
    existing = {"f": ["test_first", "test_second"]}
    for extra in ("- **Change**: rewrite", "- **Change**: rewrite\n- **Facts**:  "):
        assert "no_facts" in sheet_check(_code("f", extra=extra), _test("f"), existing)
    assert "no_facts" in sheet_check(
        _code("f", extra="- **Change**: x"), _test("f"), ["f"]
    )


def test_new_function_needs_no_facts():
    code = _code("f", extra="- **Change**: rewrite")
    assert "no_facts" not in sheet_check(code, _test("f"), {"g": ["test_first"]})
    assert "no_facts" not in sheet_check(_code("f"), _test("f"), {})


def test_sorted_unique():
    code = _code(
        "f",
        folder="src/g/",
        outputs="raise raise raise and clear it",
        extra="- **Allowed imports**: os",
    )
    test = _test("g", cases=["test_raise_once"])
    result = sheet_check(code, test, {"f": ["test_first"]})
    assert result == sorted(result)
    assert len(result) == len(set(result))
    assert len(result) >= 3
    assert "function_mismatch" in result
    assert "forbidden_field" in result


def test_change_omits_existing_case():
    code = _code("f", extra=CHANGE)
    test = _test("f", cases=["test_first"])
    existing = {"f": ["test_first", "test_second", "test_third"]}
    result = sheet_check(code, test, existing)
    assert "existing_case_missing:test_second" in result
    assert "existing_case_missing:test_third" in result
    assert "existing_case_missing:test_first" not in result


def test_change_keeps_existing_cases():
    code = _code("f", extra=CHANGE)
    test = _test("f")
    existing = {"f": ["test_first", "test_second"]}
    result = sheet_check(code, test, existing)
    assert not any(r.startswith("existing_case_missing:") for r in result)


def test_change_removes_existing_case():
    code = _code("f", extra=CHANGE)
    test = _test("f", cases=["test_first"], removed=["test_second"])
    existing = {"f": ["test_first", "test_second"]}
    result = sheet_check(code, test, existing)
    assert not any(r.startswith("existing_case_missing:") for r in result)


def test_new_function_skips_existing_case_rule():
    code = _code("f", extra=CHANGE)
    test = _test("f", cases=["test_first"])
    existing = {"g": ["test_first", "test_second"]}
    result = sheet_check(code, test, existing)
    assert not any(r.startswith("existing_case_missing:") for r in result)


def test_existing_as_names_only_skips_the_case_rule():
    code = _code("f", extra=CHANGE)
    test = _test("f", cases=["test_first"])
    result = sheet_check(code, test, ["f", "g"])
    assert not any(r.startswith("existing_case_missing:") for r in result)


def test_existing_as_names_only_still_demands_change():
    code = _code("f")
    test = _test("f", cases=["test_first"])
    assert "exists_without_change" in sheet_check(code, test, ["f"])
