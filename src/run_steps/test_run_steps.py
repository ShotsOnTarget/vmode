from datetime import UTC, datetime, timedelta

from run_steps.run_steps import run_steps

_BASE = datetime(2026, 9, 7, 19, 6, 6, 98000, tzinfo=UTC)


def _event(offset_seconds: float) -> dict:
    ts = _BASE + timedelta(seconds=offset_seconds)
    return {"ts": ts.isoformat(), "harness": "claude_code", "event": {}}


def test_two_lines_give_one_gap():
    events = [_event(0), _event(2.0)]
    assert run_steps(events) == [2.0]


def test_three_lines_give_two_gaps_in_order():
    events = [_event(0), _event(1.0), _event(3.5)]
    assert run_steps(events) == [1.0, 2.5]


def test_the_gap_is_a_float():
    events = [_event(0), _event(1.0), _event(3.5)]
    assert all(isinstance(gap, float) for gap in run_steps(events))


def test_a_gap_is_rounded_to_three_decimals():
    events = [_event(0), _event(1.23456)]
    assert run_steps(events) == [1.235]


def test_one_line_gives_an_empty_list():
    assert run_steps([_event(0)]) == []


def test_no_lines_give_an_empty_list():
    assert run_steps([]) == []


def test_lines_stamped_out_of_order_give_a_negative_gap():
    events = [_event(0), _event(-1.0)]
    assert run_steps(events) == [-1.0]
