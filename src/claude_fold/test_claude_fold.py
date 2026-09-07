from claude_fold.claude_fold import claude_fold

RESULT = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "num_turns": 1,
    "result": "ok",
    "total_cost_usd": 0.0222415,
    "usage": {
        "input_tokens": 10,
        "cache_creation_input_tokens": 10210,
        "cache_read_input_tokens": 16265,
        "output_tokens": 37,
    },
}


def test_claude_fold_sums_the_four_token_keys():
    result = claude_fold(RESULT)
    assert result["tokens"] == 26522


def test_claude_fold_takes_turns_and_cost_from_the_capture():
    result = claude_fold(RESULT)
    assert result["turns"] == 1
    assert result["cost_usd"] == 0.0222415


def test_claude_fold_returns_the_captured_report():
    result = claude_fold(RESULT)
    assert result["report"] == "ok"
    assert result["error"] is False


def test_claude_fold_flags_an_error_result():
    errored = {**RESULT, "is_error": True}
    result = claude_fold(errored)
    assert result["error"] is True


def test_claude_fold_counts_nothing_without_usage():
    no_usage = {k: v for k, v in RESULT.items() if k != "usage"}
    result = claude_fold(no_usage)
    assert result["tokens"] == -1
