import shutil
import subprocess

import pytest

from record_run.record_run import RecordError, record_run


@pytest.fixture
def bd_repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        ["bd", "init", "--prefix", "vm", "--non-interactive"],
        check=True,
        capture_output=True,
        text=True,
    )
    return tmp_path


def test_show_returns_dict(bd_repo):
    created = record_run(["create", "hello"])
    result = record_run(["show", created["id"]])
    assert isinstance(result, dict)
    assert "id" in result


def test_nonzero_exit_raises(bd_repo):
    with pytest.raises(RecordError):
        record_run(["show", "vm-nope"])


def test_missing_binary_raises(bd_repo, monkeypatch):
    monkeypatch.setenv("PATH", "")
    with pytest.raises(RecordError):
        record_run(["list"])


def test_json_flag_added(bd_repo):
    result = record_run(["list"])
    assert isinstance(result, list)
