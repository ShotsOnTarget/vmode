from sheet_cases.sheet_cases import sheet_cases

SHEET = """# Instruction sheet
- **Cases**, one test function each:
  - `test_adds`: 1 + 1 -> 2
  - `test_old`: REMOVED, superseded by test_adds
  - `test_zero`: 0 stays 0
  - `test_adds`: duplicate line
"""


def test_names_in_order():
    assert sheet_cases(SHEET) == ["adds", "zero"]


def test_removed_excluded():
    assert "old" not in sheet_cases(SHEET)


def test_no_cases_empty():
    assert sheet_cases("# Instruction sheet\n- **Signature**: x\n") == []
