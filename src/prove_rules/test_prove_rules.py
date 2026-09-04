from prove_rules.prove_rules import prove_rules

_FOLDER = "0003-4-prove_rules-test"
_NOTE = f"line1\nline2\nline3\nline4\nline5\n{_FOLDER}"
_CODE = "\n".join(f"x{i} = {i}" for i in range(9)) + "\ndef x():\n    pass\n"


def test_clean_code_empty():
    gathered = {
        "folder": _FOLDER,
        "kind": "code",
        "changed": [f"src/{_FOLDER}/x.py", f"src/{_FOLDER}/x.md"],
        "code": _CODE,
        "note": _NOTE,
        "fmt_out": "",
        "lint_out": "All checks passed!",
    }
    assert prove_rules(gathered) == []


def test_code_skips_proven():
    gathered = {
        "folder": _FOLDER,
        "kind": "code",
        "changed": [f"src/{_FOLDER}/x.py"],
        "code": _CODE,
        "note": _NOTE,
        "fmt_out": "",
        "lint_out": "All checks passed!",
        "pytest_out": "FAILED x",
        "cases": ["a"],
    }
    assert prove_rules(gathered) == []


def test_test_runs_proven():
    gathered = {
        "folder": _FOLDER,
        "kind": "test",
        "changed": [f"src/{_FOLDER}/x.py"],
        "code": _CODE,
        "note": _NOTE,
        "fmt_out": "",
        "lint_out": "All checks passed!",
        "pytest_out": "FAILED src/x/test_x.py::test_a",
        "cases": ["a"],
    }
    assert "tests_failed" in prove_rules(gathered)


def test_built_rules_first():
    gathered = {
        "folder": _FOLDER,
        "kind": "test",
        "changed": [f"src/{_FOLDER}/x.py"],
        "code": _CODE,
        "note": _NOTE,
        "fmt_out": "",
        "lint_out": "x:1:1: E501",
        "pytest_out": "FAILED src/x/test_x.py::test_a",
        "cases": ["a"],
    }
    result = prove_rules(gathered)
    assert result.index("lint_findings") < result.index("tests_failed")
