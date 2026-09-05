import subprocess

import pytest

from release_supervisor.release_supervisor import release_supervisor


def _git(path, *args):
    subprocess.run(["git", *args], cwd=path, check=True, capture_output=True)


@pytest.fixture
def repos(tmp_path):
    repo, wt = tmp_path / "repo", tmp_path / "wt"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "a.txt").write_text("1")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "-q", "-m", "one")
    _git(repo, "worktree", "add", "-q", "--detach", str(wt), "HEAD")
    (repo / "a.txt").write_text("2")
    _git(repo, "commit", "-q", "-am", "two")
    return str(repo), str(wt)


def _head(path):
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True
    ).stdout


def test_moves_when_quiet(repos):
    repo, wt = repos
    assert release_supervisor(repo, wt, {}) is True
    assert _head(wt) == _head(repo)


def test_waits_while_busy(repos):
    repo, wt = repos
    graph = {"c": {"id": "c", "kind": "code", "state": "checking"}}
    assert release_supervisor(repo, wt, graph) is False
    assert _head(wt) != _head(repo)


def test_same_path_never_moves(repos):
    repo, _ = repos
    assert release_supervisor(repo, repo, {}) is False
