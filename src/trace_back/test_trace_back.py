import os
import subprocess
import sys
from pathlib import Path

import pytest

from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from trace_back.trace_back import trace_back


def _id(created):
    return created[0]["id"] if isinstance(created, list) else created["id"]


def test_code_to_intent_order(fake_bd):
    intent = _id(
        record_run(
            ["create", "intent1", "-t", "epic", "-a", "me", "--no-inherit-labels"]
        )
    )
    story = _id(
        record_run(
            ["create", "story1", "-a", "me", "--no-inherit-labels", "--parent", intent]
        )
    )
    code = _id(
        record_run(
            ["create", "code1", "-a", "me", "--no-inherit-labels", "--parent", story]
        )
    )
    graph = record_graph()
    result = trace_back(code, graph)
    assert [r["id"] for r in result] == [code, story, intent]


def test_intent_alone(fake_bd):
    intent = _id(
        record_run(
            ["create", "intent1", "-t", "epic", "-a", "me", "--no-inherit-labels"]
        )
    )
    graph = record_graph()
    result = trace_back(intent, graph)
    assert [r["id"] for r in result] == [intent]


def test_unknown_id_raises(fake_bd):
    record_run(["create", "intent1", "-t", "epic", "-a", "me", "--no-inherit-labels"])
    with pytest.raises(ValueError):
        trace_back("vm-none", record_graph())


def test_cycle_raises():
    script = (
        "from trace_back.trace_back import trace_back as t\n"
        "g = {'a': {'id': 'a', 'parent': 'b'}, 'b': {'id': 'b', 'parent': 'a'}}\n"
        "try:\n    t('a', g)\nexcept ValueError:\n    pass\n"
        "else:\n    raise SystemExit(1)\n"
    )
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent)}
    result = subprocess.run([sys.executable, "-c", script], timeout=1, env=env)
    assert result.returncode == 0
