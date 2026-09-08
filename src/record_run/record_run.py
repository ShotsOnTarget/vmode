import copy
import json
import os
import shutil
import subprocess
import time

_READS = (("list",), ("show",), ("comments",), ("label", "list"))
_TTL = 1.5
_cache: dict[tuple, tuple[float, object]] = {}


class RecordError(Exception):
    def __init__(self, message: str, stderr: str):
        super().__init__(message)
        self.message = message
        self.stderr = stderr


def _is_read(args: list[str]) -> bool:
    return any(tuple(args[: len(v)]) == v for v in _READS)


def record_run(args: list[str]) -> dict | list:
    """Run one record command and return its parsed JSON.

    The record is the `bd` client, called with --json: the path in VMODE_BD
    when set (so every shell resolves the same client), else `bd` on PATH.
    VMODE_RECORD=fake sends the call to the in-memory fake record instead,
    so unit tests never start a database. Raises RecordError when the client
    is missing, exits non-zero, or prints something not JSON.

    A read repeated within 1.5 seconds is answered from memory and any write
    empties that memory first, so a read never sees data older than this
    process's last write. That window is shorter than one whole-record read,
    so it catches a graph and its labels (one query, asked twice) and little
    else; another process's write can be that stale."""
    if not _is_read(list(args)):
        _cache.clear()
        return _dispatch(args)
    key = tuple(args)
    hit = _cache.get(key)
    if hit is not None and time.monotonic() - hit[0] < _TTL:
        return copy.deepcopy(hit[1])
    value = _dispatch(args)
    _cache[key] = (time.monotonic(), value)
    return copy.deepcopy(value)


def _dispatch(args: list[str]) -> dict | list:
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
