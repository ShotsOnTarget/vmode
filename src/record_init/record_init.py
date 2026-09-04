import os
import subprocess

from record_run.record_run import RecordError


def record_init(path: str) -> dict:
    if not os.path.isdir(path):
        raise RecordError("directory does not exist", "")

    port = os.environ.get("BD_SERVER_PORT")
    if not port:
        raise RecordError("BD_SERVER_PORT is not set", "")

    args = [
        "bd",
        "init",
        "--prefix",
        "vm",
        "--non-interactive",
        "--server",
        "--server-port",
        port,
    ]

    try:
        result = subprocess.run(
            args,
            cwd=path,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RecordError("failed to run bd init", str(exc)) from exc

    if result.returncode != 0:
        raise RecordError("bd init exited non-zero", result.stderr)

    return {"path": path, "prefix": "vm"}
