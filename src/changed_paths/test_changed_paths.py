import subprocess
from pathlib import Path

from changed_paths.changed_paths import changed_paths


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "a@a.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "a"], cwd=path, check=True)


def test_reports_changed_paths_inside_and_outside_src(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "x").mkdir(parents=True)
    (tmp_path / "src" / "x" / "x.py").write_text("x")
    (tmp_path / "roles" / "shared").mkdir(parents=True)
    (tmp_path / "roles" / "shared" / "report-format.md").write_text("t")

    result = changed_paths("x", {}, repo=str(tmp_path))

    assert result == ["roles/shared/report-format.md", "src/x/x.py"]


def test_excludes_paths_claimed_by_another_active_job(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "src" / "x").mkdir(parents=True)
    (tmp_path / "src" / "x" / "x.py").write_text("x")
    (tmp_path / "src" / "y").mkdir(parents=True)
    (tmp_path / "src" / "y" / "y.py").write_text("y")
    graph = {"0001": {"kind": "test", "title": "y test", "state": "in_progress"}}

    result = changed_paths("x", graph, repo=str(tmp_path))

    assert result == ["src/x/x.py"]
