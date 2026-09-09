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


def test_over_80():
    lines = "\n".join(f"x{i} = {i}" for i in range(81))
    assert "over_80_lines" in gate_built(JOB, _inputs(code=lines))


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


def test_file_outside_src_is_seen():
    """Before 2026-09-08 a path outside src was filtered out before the gate."""
    changed = [f"src/{JOB}/x.py", "roles/shared/report-format.md"]
    assert "file_outside_folder" in gate_built(JOB, _inputs(changed=changed))


def test_markdown_touched():
    """A Builder writes code and tests, never documentation."""
    changed = [f"src/{JOB}/x.py", "roles/builder/SKILL.md"]
    assert "markdown_touched" in gate_built(JOB, _inputs(changed=changed))


def test_no_markdown_no_rule():
    assert "markdown_touched" not in gate_built(JOB, _inputs())


def test_three_files_in_the_folder_too_many_whatever_changed():
    """A third file that landed earlier still fails: the folder is counted."""
    files = ["x.py", "test_x.py", "__main__.py"]
    assert "too_many_files" in gate_built(JOB, _inputs(files=files))
    assert "too_many_files" not in gate_built(JOB, _inputs(files=files[:2]))


def test_suppression_comment_named():
    """A comment that silences the tools is refused; the tools decide."""
    lines = (
        "# ruff: noqa: E501",
        "# fmt: off",
        "x = 1  # noqa",
        "y = 2  # type: ignore",
    )
    for line in lines:
        assert "suppressed_lint" in gate_built(JOB, _inputs(code=GOOD + line + "\n"))
    assert "suppressed_lint" not in gate_built(JOB, _inputs())
