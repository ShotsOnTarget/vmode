from log_append.log_append import log_append
from log_read_item.log_read_item import log_read_item


def _entry(item, gate, tokens=1):
    return {
        "item": item,
        "gate": gate,
        "rule": "r",
        "inputs": "i",
        "state": "s",
        "tokens": tokens,
        "seconds": 0,
        "actor": "builder",
    }


def test_returns_in_order(bd_repo):
    log_append(_entry("A", "Built"))
    log_append(_entry("A", "Proven"))
    log_append(_entry("A", "Verified"))

    result = log_read_item("A")

    assert [r["gate"] for r in result] == ["built", "proven", "verified"]


def test_other_target_excluded(bd_repo):
    log_append(_entry("B", "Built"))

    result = log_read_item("A")

    assert result == []


def test_none_empty(bd_repo):
    result = log_read_item("A")

    assert result == []


def test_payload_merged(bd_repo):
    log_append(_entry("A", "Built", tokens=42))

    result = log_read_item("A")

    assert result[0]["tokens"] == 42
