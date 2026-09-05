import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from find_orphans.find_orphans import find_orphans
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from record_set_state.record_set_state import record_set_state


def _id(c):
    return c[0]["id"] if isinstance(c, list) else c["id"]


def _mk(title, kind, parent=None):
    a = ["create", title, "-a", "me", "--no-inherit-labels", "-l", f"kind:{kind}"]
    a += (["--parent", parent] if parent else []) + (
        ["-t", "epic"] if kind == "intent" else []
    )
    return _id(record_run(a))


def _val(a, b):
    record_run(["dep", "add", a, b, "-t", "validates"])


def test_story_without_verification(fake_bd):
    intent = _mk("intent1", "intent")
    story = _mk("story1", "story", intent)
    _val(_mk("validation1", "validation"), intent)
    assert {"id": story, "rule": "unchecked"} in find_orphans(record_graph())


def test_test_without_checks(fake_bd):
    intent = _mk("intent1", "intent")
    story = _mk("story1", "story", intent)
    verification = _mk("verification1", "verification")
    validation = _mk("validation1", "validation")
    code = _mk("code1", "code", story)
    test_item = _mk("test1", "test")
    _val(verification, story)
    _val(validation, intent)
    r = find_orphans(record_graph())
    assert {"id": test_item, "rule": "checks_nothing"} in r and {
        "id": code,
        "rule": "unchecked",
    } in r


def test_story_without_parent():
    graph = {"story1": {"id": "story1", "kind": "story", "parent": None, "checks": []}}
    assert {"id": "story1", "rule": "no_parent"} in find_orphans(graph)


def test_clean_graph_empty(fake_bd):
    other = _mk("other_intent", "intent")
    intent = _mk("intent1", "intent")
    story = _mk("story1", "story", intent)
    code = _mk("code1", "code", story)
    test_item = _mk("test1", "test", story)
    verification = _mk("verification1", "verification", intent)
    validation = _mk("validation1", "validation", other)
    _val(test_item, code)
    _val(test_item, other)
    _val(verification, story)
    _val(validation, intent)
    assert find_orphans(record_graph()) == []


def test_proposal_unchecked():
    graph = {
        "story1": {"id": "story1", "kind": "story", "parent": None, "checks": []},
        "proposal1": {
            "id": "proposal1",
            "kind": "proposal",
            "parent": "story1",
            "checks": [],
        },
    }
    assert {"id": "proposal1", "rule": "unchecked"} in find_orphans(graph)


def test_note_not_orphan(fake_bd):
    intent = _mk("intent1", "intent")
    code = _mk("code1", "code", intent)
    record_set_state(code, "done")
    note = _mk("saw X", "note", code)
    assert note not in [o["id"] for o in find_orphans(record_graph())]


@pytest.mark.integration
def test_script_exit_code(bd_repo):
    _mk("intent1", "intent")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    proc = subprocess.run(
        [sys.executable, "-m", "find_orphans.find_orphans"],
        cwd=bd_repo,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 1
    json.loads(proc.stdout)
