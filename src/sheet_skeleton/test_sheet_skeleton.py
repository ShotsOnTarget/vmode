from sheet_skeleton.sheet_skeleton import sheet_skeleton


def test_code_skeleton_exact():
    job = {"id": "a", "kind": "code", "parent": "p", "title": "f code"}
    expected = (
        "# Instruction sheet\n"
        "\n"
        "- **Job id**: a\n"
        "- **Kind**: code\n"
        "- **Parent Story**: p\n"
        "- **Function name**: `f`\n"
        "- **Folder**: `src/f/`\n"
        "- **Signature**: \n"
        "- **Inputs**: \n"
        "- **Outputs**: \n"
        "- **Checklist items this job serves**: \n"
    )
    result = sheet_skeleton(job)
    assert result == expected
    assert result.endswith("\n") and not result.endswith("\n\n")
    assert "- **Cases**:" not in result


def test_test_skeleton_has_cases_line():
    job = {"id": "a", "kind": "test", "parent": "p", "title": "f test"}
    assert sheet_skeleton(job).endswith("- **Cases**:\n")


def test_serves_joined():
    job = {
        "id": "a",
        "kind": "code",
        "parent": "p",
        "title": "f code",
        "serves": ["1", "3"],
    }
    assert "- **Checklist items this job serves**: 1, 3\n" in sheet_skeleton(job)


def test_missing_serves_empty():
    job = {"id": "a", "kind": "code", "parent": "p", "title": "f code"}
    result = sheet_skeleton(job)
    assert result.endswith("- **Checklist items this job serves**: \n")


def test_bad_kind_raises():
    job = {"id": "a", "kind": "story", "parent": "p", "title": "f story"}
    try:
        sheet_skeleton(job)
    except ValueError:
        caught = True
    else:
        caught = False
    assert caught


def test_title_kind_mismatch_raises():
    job = {"id": "a", "kind": "code", "parent": "p", "title": "f test"}
    try:
        sheet_skeleton(job)
    except ValueError:
        caught = True
    else:
        caught = False
    assert caught


def test_space_in_function_raises():
    job = {"id": "a", "kind": "code", "parent": "p", "title": "two words code"}
    try:
        sheet_skeleton(job)
    except ValueError:
        caught = True
    else:
        caught = False
    assert caught
