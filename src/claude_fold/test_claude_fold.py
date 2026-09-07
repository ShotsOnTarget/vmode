import json
import pathlib

import pytest

from claude_fold.claude_fold import claude_fold

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT = json.loads((ROOT / "fixtures" / "claude_run.json").read_text(encoding="utf-8"))

SYSTEM_EVENT = {"type": "system", "subtype": "init"}
ASSISTANT_EVENT = {"type": "assistant", "message": {"content": []}}
STREAM = [SYSTEM_EVENT, ASSISTANT_EVENT, RESULT]


def test_claude_fold_sums_the_four_token_keys():
    result = claude_fold(STREAM)
    assert result["tokens"] == 26522


def test_claude_fold_takes_turns_and_cost_from_the_capture():
    result = claude_fold(STREAM)
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.0222415


def test_claude_fold_returns_the_captured_report():
    result = claude_fold(STREAM)
    assert result["report"] == "ok"
    assert result["error"] is False


def test_claude_fold_flags_an_error_result():
    errored = {**RESULT, "is_error": True}
    result = claude_fold([SYSTEM_EVENT, ASSISTANT_EVENT, errored])
    assert result["error"] is True


def test_claude_fold_counts_nothing_without_usage():
    no_usage = {k: v for k, v in RESULT.items() if k != "usage"}
    result = claude_fold([SYSTEM_EVENT, ASSISTANT_EVENT, no_usage])
    assert result["tokens"] == -1


def test_claude_fold_reads_the_result_event_of_a_stream():
    from_stream = claude_fold(STREAM)
    from_result_alone = claude_fold([RESULT])
    assert from_stream == from_result_alone


def test_claude_fold_takes_the_last_result_event():
    second = {**RESULT, "num_turns": 9}
    result = claude_fold([SYSTEM_EVENT, ASSISTANT_EVENT, RESULT, second])
    assert result["turns"] == 9


def test_claude_fold_without_a_result_event_ends_in_valueerror():
    with pytest.raises(ValueError):
        claude_fold([SYSTEM_EVENT, ASSISTANT_EVENT])
