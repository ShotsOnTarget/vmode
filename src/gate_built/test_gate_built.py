import pytest

from gate_built.gate_built import gate_built

JOB = "0003-1-gate_built-test"
GOOD = 'def x():\n    """Do x."""\n    return 1\n'


def _inputs(**over):
    base = {
        "changed": [f"src/{JOB}/x.py"],
        "code": GOOD,
        "fmt_out": "",
        "lint_out": "All checks passed!",
    }
    base.update(over)
    return base


def test_outside_folder():
    assert "file_outside_folder" in gate_built(JOB, _inputs(changed=["src/other/x.py"]))


def test_over_50():
    lines = "\n".join(f"x{i} = {i}" for i in range(51))
    assert "over_50_lines" in gate_built(JOB, _inputs(code=lines))


def test_not_formatted():
    assert "not_formatted" in gate_built(JOB, _inputs(fmt_out="--- a\n+++ b\n"))


def test_lint_findings():
    assert "lint_findings" in gate_built(JOB, _inputs(lint_out="x.py:1:1: E501"))


def test_clean_passes():
    assert gate_built(JOB, _inputs()) == []


def test_no_docstring():
    assert "no_docstring" in gate_built(JOB, _inputs(code="def x():\n    pass\n"))


def test_three_files_too_many():
    changed = [f"src/{JOB}/x.py", f"src/{JOB}/test_x.py", f"src/{JOB}/x.md"]
    assert "too_many_files" in gate_built(JOB, _inputs(changed=changed))


def test_syntax_error_raises():
    with pytest.raises(ValueError):
        gate_built(JOB, _inputs(code="def x(:\n"))
