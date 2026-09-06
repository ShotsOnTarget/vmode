import pytest
from summary_lines.summary_lines import summary_lines


def test_eight_lines_in_order():
    outcome = {"action": "escalate", "retries": 3, "rules": ["a", "b"]}
    assert summary_lines("vm-1", outcome, "engineer") == [
        "- **Work item id**: vm-1",
        "- **From**: Supervisor",
        "- **For**: engineer",
        "- **What failed**: gate checks did not pass.",
        "- **How many times**: 3",
        "- **Which rule or gate**: a, b",
        "- **What was already tried**: escalated 3 time(s).",
        "- **Decision needed**: engineer: split the pair or rewrite "
        "the sheet; if the Story checklist must change, "
        "raise it to the architect.",
    ]


def test_for_line_names_recipient():
    outcome = {"action": "escalate", "retries": 3, "rules": ["a", "b"]}
    assert summary_lines("vm-1", outcome, "architect")[2] == "- **For**: architect"


def test_decision_names_recipient():
    outcome = {"action": "escalate", "retries": 3, "rules": ["a", "b"]}
    last = summary_lines("vm-1", outcome, "engineer")[-1]
    assert last.startswith("- **Decision needed**: engineer:")


def test_bounce_wording():
    outcome = {"action": "bounce", "retries": 1, "rules": ["a"]}
    lines = summary_lines("vm-1", outcome, "engineer")
    assert "- **What was already tried**: bounced 1 time(s)." in lines


def test_bad_action_raises():
    outcome = {"action": "retry", "retries": 1, "rules": ["a"]}
    with pytest.raises(ValueError):
        summary_lines("vm-1", outcome, "engineer")
