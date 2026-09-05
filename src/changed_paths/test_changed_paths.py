import subprocess
from pathlib import Path

import pytest

from changed_paths.changed_paths import changed_paths


def _run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True)


def _init_repo(path: Path) -> None:
    _run(["git", "init", "-q"], path)
    _run(["git", "config", "user.email", "a@a.com"], path)
    _run(["git", "config", "user.name", "a"], path)


def test_only_src_paths(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "x").mkdir(parents=True)
    (tmp_path / "src" / "x" / "x.py").write_text("x")
    (tmp_path / "work").mkdir()
    (tmp_path / "work" / "log.jsonl").write_text("log")

    result = changed_paths("src", {}, repo=str(tmp_path))

    assert result == ["src/x/x.py"]


def test_other_claimed_folder_dropped(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "x").mkdir(parents=True)
    (tmp_path / "src" / "x" / "x.py").write_text("x")
    (tmp_path / "src" / "y").mkdir(parents=True)
    (tmp_path / "src" / "y" / "y.py").write_text("y")

    graph = {
        "0001": {
            "id": "0001",
            "kind": "code",
            "title": "y code",
            "owner": "",
            "state": "in_progress",
            "parent": None,
            "checks": [],
            "needs": [],
        }
    }

    result = changed_paths("src", graph, repo=str(tmp_path))

    assert result == ["src/x/x.py"]


def test_other_unclaimed_folder_kept(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "x").mkdir(parents=True)
    (tmp_path / "src" / "x" / "x.py").write_text("x")
    (tmp_path / "src" / "y").mkdir(parents=True)
    (tmp_path / "src" / "y" / "y.py").write_text("y")

    graph = {
        "0001": {
            "id": "0001",
            "kind": "code",
            "title": "y code",
            "owner": "",
            "state": "done",
            "parent": None,
            "checks": [],
            "needs": [],
        }
    }

    result = changed_paths("src", graph, repo=str(tmp_path))

    assert result == sorted(["src/x/x.py", "src/y/y.py"])


def test_rename_uses_new_path(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "x").mkdir(parents=True)
    (tmp_path / "src" / "x" / "a.py").write_text("a")
    _run(["git", "add", "."], tmp_path)
    _run(["git", "commit", "-q", "-m", "init"], tmp_path)
    _run(["git", "mv", "src/x/a.py", "src/x/b.py"], tmp_path)

    result = changed_paths("src", {}, repo=str(tmp_path))

    assert "src/x/b.py" in result
    assert "src/x/a.py" not in result


def test_git_failure_raises(tmp_path):
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()

    with pytest.raises(RuntimeError):
        changed_paths("src", {}, repo=str(not_a_repo))


def test_bounced_folder_is_claimed(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "other").mkdir(parents=True)
    (tmp_path / "src" / "other" / "other.py").write_text("o")

    graph = {
        "0001": {
            "id": "0001",
            "kind": "code",
            "title": "other code",
            "owner": "",
            "state": "ready",
            "parent": None,
            "checks": [],
            "needs": [],
        }
    }

    result = changed_paths("mine", graph, repo=str(tmp_path))

    assert "src/other/other.py" not in result
