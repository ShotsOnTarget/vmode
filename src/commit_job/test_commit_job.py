import subprocess
from pathlib import Path

import pytest

from commit_job.commit_job import commit_job


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    src_x = repo / "src" / "x"
    src_x.mkdir(parents=True)
    (src_x / "file.txt").write_text("hello")
    return repo


def test_commits_only_folder(tmp_path):
    repo = _init_repo(tmp_path)
    src_y = repo / "src" / "y"
    src_y.mkdir(parents=True)
    (src_y / "file.txt").write_text("world")

    result = commit_job("vm-1", "x", str(repo))

    assert result
    show = subprocess.run(
        ["git", "show", "--stat", "--format=", result],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "src/x" in show.stdout
    assert "src/y" not in show.stdout

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "src/y" in status.stdout


def test_message_names_job(tmp_path):
    repo = _init_repo(tmp_path)

    result = commit_job("vm-1", "x", str(repo))

    log = subprocess.run(
        ["git", "log", "-1", "--format=%B", result],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    message = log.stdout
    assert "Job: vm-1" in message
    assert message.startswith("x: job vm-1")


def test_nothing_to_commit_none(tmp_path):
    repo = _init_repo(tmp_path)
    commit_job("vm-1", "x", str(repo))

    result = commit_job("vm-1", "x", str(repo))

    assert result is None


def test_git_failure_raises(tmp_path):
    not_repo = tmp_path / "not_a_repo"
    not_repo.mkdir()
    (not_repo / "src").mkdir()
    (not_repo / "src" / "x").mkdir()

    with pytest.raises(RuntimeError):
        commit_job("vm-1", "x", str(not_repo))
