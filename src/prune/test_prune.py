import subprocess

import pytest

from prune.prune import prune


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "src" / "w").mkdir(parents=True)
    (tmp_path / "src" / "w" / "w.py").write_text("def w():\n    pass\n")
    return str(tmp_path)


def _graph(state):
    return {
        "i": {
            "id": "i",
            "kind": "intent",
            "title": "I",
            "state": "done",
            "parent": None,
            "checks": [],
        },
        "v": {
            "id": "v",
            "kind": "validation",
            "title": "V",
            "state": "done",
            "parent": "i",
            "checks": ["i"],
        },
        "c": {
            "id": "c",
            "kind": "code",
            "title": "w code",
            "state": state,
            "parent": "i",
            "checks": [],
        },
        "t": {
            "id": "t",
            "kind": "test",
            "title": "w test",
            "state": "done",
            "parent": "i",
            "checks": ["c"],
        },
    }


def test_leftover_files_named(repo):
    rules = [f["rule"] for f in prune(_graph("done"), repo)]
    assert "leftover_files" in rules


def test_open_job_owns_its_files(repo):
    rules = [f["rule"] for f in prune(_graph("in_progress"), repo)]
    assert "leftover_files" not in rules


def test_folder_without_item(repo):
    graph = {k: v for k, v in _graph("done").items() if k not in ("c", "t")}
    found = [f for f in prune(graph, repo) if f["rule"] == "no_record_item"]
    assert found and found[0]["target"] == "w"


def test_orphans_included(repo):
    graph = _graph("done")
    graph["s"] = {
        "id": "s",
        "kind": "story",
        "title": "S",
        "state": "done",
        "parent": None,
        "checks": [],
    }
    assert any(f["target"] == "s" for f in prune(graph, repo))
