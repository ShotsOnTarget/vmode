import socket
import subprocess
import time

import pytest


@pytest.fixture
def bd_repo(tmp_path, monkeypatch):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    dolt_dir = tmp_path / "dolt"
    repo = tmp_path / "repo"
    dolt_dir.mkdir()
    repo.mkdir()

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
    connected = False
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                connected = True
                break
        except OSError:
            time.sleep(0.1)

    if not connected:
        server.terminate()
        server.wait()
        raise RuntimeError(
            f"dolt sql-server did not accept connections on port {port} within 15 seconds"
        )

    try:
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(
            [
                "bd",
                "init",
                "--prefix",
                "vm",
                "--non-interactive",
                "--server",
                "--server-port",
                str(port),
            ],
            cwd=repo,
            check=True,
        )
        monkeypatch.chdir(repo)
        yield repo
    finally:
        server.terminate()
        server.wait()
