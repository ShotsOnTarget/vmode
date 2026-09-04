import pytest

from step.step import step


def test_fail_retries_two():
    assert step("checking", "gate_fail", 2) == ("bounce", "ready", 3)


def test_fail_retries_three():
    assert step("checking", "gate_fail", 3) == ("escalate", "blocked", 3)


def test_sheet_changed_resets():
    assert step("blocked", "sheet_changed", 5) == ("reset", "waiting", 0)


def test_pass_done():
    assert step("checking", "gate_pass", 1) == ("log_done", "done", 1)


def test_unknown_raises():
    with pytest.raises(ValueError):
        step("done", "gate_fail", 0)
