import json
import pathlib

from opencode_fold.opencode_fold import opencode_fold

ROOT = pathlib.Path(__file__).resolve().parents[2]
ERROR_EVENT = json.loads(
    (ROOT / "fixtures" / "opencode_error_event.json").read_text(encoding="utf-8")
)
EVENTS = [
    json.loads(line)
    for line in (ROOT / "fixtures" / "opencode_run.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
    if line.strip()
]


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


def test_opencode_fold_tolerates_a_step_without_total():
    """A step_finish whose tokens carry no total counts as zero, never raises."""
    odd = {"type": "step_finish", "part": {"tokens": {"input": 3}, "cost": 0.1}}
    result = opencode_fold(EVENTS + [odd])
    assert result["tokens"] == 29524
    assert result["turns"] == 3
    assert result["error"] is False
