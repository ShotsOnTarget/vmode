import itertools
import socket
import subprocess
import time

import pytest

_COUNTER = itertools.count()


@pytest.fixture(autouse=True)
def _empty_record_cache():
    """record_run remembers a read for a moment and forgets it on any write.
    A fixture that swaps the whole record underneath it is not a write, so
    every test starts and ends with that memory empty."""
    from record_run.record_run import _cache

    _cache.clear()
    yield
    _cache.clear()


@pytest.fixture
def fake_bd(tmp_path, monkeypatch):
    """The in-memory record: VMODE_RECORD=fake, reset per test, cwd a fresh git repo."""
    from fake_record.fake_record import fake_record

    fake_record(["__reset__"])
    monkeypatch.setenv("VMODE_RECORD", "fake")
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    monkeypatch.chdir(repo)
    yield repo


@pytest.fixture(scope="session")
def dolt_server(tmp_path_factory):
    """One Dolt server for the whole test session; each test gets its own database."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    dolt_dir = tmp_path_factory.mktemp("dolt")
    server = subprocess.Popen(
        [
            "dolt",
            "sql-server",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--data-dir",
            str(dolt_dir),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            time.sleep(0.1)
    else:
        server.terminate()
        server.wait()
        raise RuntimeError(f"dolt sql-server did not accept connections on port {port}")
    yield port
    server.terminate()
    server.wait()


@pytest.fixture
def bd_repo(tmp_path, monkeypatch, dolt_server):
    """Integration only: a fresh git repo with a real record database."""
    monkeypatch.delenv("VMODE_RECORD", raising=False)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    name = f"t{next(_COUNTER)}_{tmp_path.name.replace('-', '_')}"[:40]
    subprocess.run(
        [
            "bd",
            "init",
            "--prefix",
            "vm",
            "--non-interactive",
            "--server",
            "--server-port",
            str(dolt_server),
            "--database",
            name,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    monkeypatch.chdir(repo)
    yield repo
