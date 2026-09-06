import json
import os
import shutil
import subprocess


class RecordError(Exception):
    def __init__(self, message: str, stderr: str):
        super().__init__(message)
        self.message = message
        self.stderr = stderr


def record_run(args: list[str]) -> dict | list:
    """Run one record command and return its parsed JSON.

    The record is the `bd` client, called with --json: the path in VMODE_BD
    when set (so every shell resolves the same client), else `bd` on PATH.
    When the
    environment names VMODE_RECORD=fake the call goes to the in-memory fake
    record instead, so unit tests never start a database; the fake answers
    with the same shapes, captured from real runs. Raises RecordError when
    the client is missing, exits non-zero, or prints something not JSON.
    """
    if os.environ.get("VMODE_RECORD") == "fake":
        from fake_record.fake_record import fake_record

        try:
            return fake_record(list(args))
        except (KeyError, LookupError, ValueError) as exc:
            raise RecordError("fake record refused", str(exc)) from exc
    return _run_bd(args)


def _run_bd(args: list[str]) -> dict | list:
    client = os.environ.get("VMODE_BD") or "bd"
    if shutil.which(client) is None:
        raise RecordError(f"record client not found: {client}", "")
    try:
        result = subprocess.run(
            [client, *args, "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise RecordError("failed to run bd", str(exc)) from exc
    if result.returncode != 0:
        raise RecordError("bd exited non-zero", result.stderr)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RecordError("bd printed non-JSON output", result.stderr) from exc
