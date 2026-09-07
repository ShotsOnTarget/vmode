from opencode_fold.opencode_fold import opencode_fold

EVENTS = [
    {"type": "step_start", "timestamp": 1788798823174, "part": {"type": "step-start"}},
    {
        "type": "text",
        "timestamp": 1788798827521,
        "part": {
            "type": "text",
            "text": "Using glob to list the policy folder for file count.",
        },
    },
    {
        "type": "tool_use",
        "timestamp": 1788798827685,
        "part": {
            "type": "tool",
            "tool": "glob",
            "state": {"status": "completed", "input": {"pattern": "policy/*"}},
        },
    },
    {
        "type": "step_finish",
        "timestamp": 1788798828230,
        "part": {
            "reason": "tool-calls",
            "type": "step-finish",
            "tokens": {
                "total": 14701,
                "input": 14102,
                "output": 69,
                "reasoning": 530,
                "cache": {"write": 0, "read": 0},
            },
            "cost": 0,
        },
    },
    {"type": "step_start", "timestamp": 1788798830651, "part": {"type": "step-start"}},
    {
        "type": "text",
        "timestamp": 1788798830683,
        "part": {"type": "text", "text": "1"},
    },
    {
        "type": "step_finish",
        "timestamp": 1788798831328,
        "part": {
            "reason": "stop",
            "type": "step-finish",
            "tokens": {
                "total": 14823,
                "input": 673,
                "output": 11,
                "reasoning": 74,
                "cache": {"write": 0, "read": 14065},
            },
            "cost": 0,
        },
    },
]

ERROR_EVENT = {
    "type": "error",
    "timestamp": 1788624094161,
    "error": {"name": "APIError", "data": {"message": "No payment method."}},
}


def test_opencode_fold_counts_a_captured_run():
    result = opencode_fold(EVENTS)
    assert result["tokens"] == 29524
    assert result["turns"] == 2


def test_opencode_fold_sums_the_captured_cost():
    result = opencode_fold(EVENTS)
    assert result["cost_usd"] is not None
    assert result["cost_usd"] == 0.0


def test_opencode_fold_joins_the_captured_text():
    result = opencode_fold(EVENTS)
    assert result["report"] == (
        "Using glob to list the policy folder for file count.\n1"
    )
    assert result["error"] is False


def test_opencode_fold_flags_a_captured_error():
    result = opencode_fold(EVENTS + [ERROR_EVENT])
    assert result["error"] is True
    last_line = result["report"].splitlines()[-1]
    assert last_line.startswith("ERROR: ")
    assert "APIError" in last_line


def test_opencode_fold_counts_nothing_without_a_step():
    result = opencode_fold(EVENTS[:3])
    assert result["tokens"] == -1
    assert result["turns"] is None
    assert result["cost_usd"] is None
