import pytest

from gate_built.gate_built import gate_built


def test_outside_folder():
    result = gate_built(
        "0003-1-gate_built-test",
        {
            "changed": ["src/other/x.py"],
            "code": "def x():\n    pass\n",
            "note": "line1\nline2\nline3\nline4\nline5\n0003-1-gate_built-test",
            "fmt_out": "",
            "lint_out": "All checks passed!",
        },
    )
    assert "file_outside_folder" in result


def test_over_50():
    lines = "\n".join(f"x{i} = {i}" for i in range(51))
    result = gate_built(
        "0003-1-gate_built-test",
        {
            "changed": ["src/0003-1-gate_built-test/x.py"],
            "code": lines,
            "note": "line1\nline2\nline3\nline4\nline5\n0003-1-gate_built-test",
            "fmt_out": "",
            "lint_out": "All checks passed!",
        },
    )
    assert "over_50_lines" in result


def test_not_formatted():
    result = gate_built(
        "0003-1-gate_built-test",
        {
            "changed": ["src/0003-1-gate_built-test/x.py"],
            "code": "def x():\n    pass\n",
            "note": "line1\nline2\nline3\nline4\nline5\n0003-1-gate_built-test",
            "fmt_out": "would reformat src/x/x.py",
            "lint_out": "All checks passed!",
        },
    )
    assert "not_formatted" in result


def test_lint_findings():
    result = gate_built(
        "0003-1-gate_built-test",
        {
            "changed": ["src/0003-1-gate_built-test/x.py"],
            "code": "def x():\n    pass\n",
            "note": "line1\nline2\nline3\nline4\nline5\n0003-1-gate_built-test",
            "fmt_out": "",
            "lint_out": "src/x/x.py:1:1: E501 line too long",
        },
    )
    assert "lint_findings" in result


def test_clean_passes():
    result = gate_built(
        "0003-1-gate_built-test",
        {
            "changed": [
                "src/0003-1-gate_built-test/x.py",
                "src/0003-1-gate_built-test/x.md",
            ],
            "code": "\n".join(f"x{i} = {i}" for i in range(9))
            + "\ndef x():\n    pass\n",
            "note": "line1\nline2\nline3\nline4\nline5\n0003-1-gate_built-test",
            "fmt_out": "",
            "lint_out": "All checks passed!",
        },
    )
    assert result == []


def test_syntax_error_raises():
    with pytest.raises(ValueError):
        gate_built(
            "0003-1-gate_built-test",
            {
                "changed": ["src/0003-1-gate_built-test/x.py"],
                "code": "def (",
                "note": "line1\nline2\nline3\nline4\nline5\n0003-1-gate_built-test",
                "fmt_out": "",
                "lint_out": "All checks passed!",
            },
        )
