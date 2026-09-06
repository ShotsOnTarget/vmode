from sheet_fields.sheet_fields import sheet_fields


def test_fields_keyed_and_stripped():
    assert sheet_fields("- **Kind**:  code ") == {"kind": "code", "cases": []}


def test_key_drops_parenthetical_and_spaces():
    sheet = "- **Cases (test jobs only)**:\n- **Checklist items this job serves**: 1\n"
    result = sheet_fields(sheet)
    assert result["checklist_items_this_job_serves"] == "1"
    assert result["cases"] == []


def test_continuation_lines_join_value():
    sheet = "- **Inputs**: a\n  continued\n  more\n"
    assert sheet_fields(sheet)["inputs"] == "a\ncontinued\nmore"


def test_cases_listed_in_order():
    sheet = "- **Cases**:\n  - `test_b`: x\n  - `test_a`: y\n"
    assert sheet_fields(sheet)["cases"] == ["test_b", "test_a"]


def test_cases_empty_without_field():
    assert sheet_fields("- **Kind**: code\n")["cases"] == []


def test_no_fields_returns_empty():
    assert sheet_fields("") == {}
    assert sheet_fields("just some prose\nmore prose\n") == {}


def test_duplicate_field_last_wins():
    sheet = "- **Kind**: code\n- **Kind**: test\n"
    assert sheet_fields(sheet)["kind"] == "test"
