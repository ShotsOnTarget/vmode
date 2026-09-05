import json
import shutil
import subprocess


class RecordError(Exception):
    def __init__(self, message: str, stderr: str):
        super().__init__(message)
        self.message = message
        self.stderr = stderr


def record_run(args: list[str]) -> dict | list:
    """Run the `bd` CLI with given arguments and return its parsed JSON output."""
    if shutil.which("bd") is None:
        raise RecordError("bd is not on PATH", "")

    full_args = ["bd"] + list(args) + ["--json"]

    try:
        result = subprocess.run(
            full_args,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise RecordError("failed to run bd", str(exc)) from exc

    if result.returncode != 0:
        raise RecordError("bd exited non-zero", result.stderr)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RecordError("bd printed non-JSON output", result.stderr) from exc
