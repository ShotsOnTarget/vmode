import json
import subprocess

from record_init.record_init import record_init
from record_run.record_run import RecordError


def _set_port(monkeypatch, bd_repo):
    port = (bd_repo / ".beads" / "dolt-server.port").read_text().strip()
    monkeypatch.setenv("BD_SERVER_PORT", port)


def test_empty_dir_inits(tmp_path, monkeypatch, bd_repo):
    _set_port(monkeypatch, bd_repo)
    target = tmp_path / "fresh"
    target.mkdir()

    result = record_init(str(target))

    assert result == {"path": str(target), "prefix": "vm"}
    assert (target / ".beads").exists()


def test_list_is_empty_after_init(tmp_path, monkeypatch, bd_repo):
    _set_port(monkeypatch, bd_repo)
    target = tmp_path / "fresh2"
    target.mkdir()

    record_init(str(target))

    result = subprocess.run(
        ["bd", "list", "--json"],
        cwd=target,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout) == []


def test_missing_dir_raises(tmp_path, monkeypatch, bd_repo):
    _set_port(monkeypatch, bd_repo)
    missing = tmp_path / "nope"

    try:
        record_init(str(missing))
        assert False, "expected RecordError"
    except RecordError:
        pass
