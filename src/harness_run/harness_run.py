import subprocess
import time


def harness_run(argv: list[str], cwd: str, timeout: int = 1800) -> dict:
    """Run one harness command and capture its result.

    argv: the full command line, executable first. cwd: the directory the
    child runs in. timeout: whole seconds the child is allowed before it is
    killed; default 1800. Returns a dict with stdout (str), stderr (str),
    returncode (int, as-is), and seconds (float, wall-clock time around the
    child run). A child that outlives timeout lets subprocess.TimeoutExpired
    reach the caller.
    """
    start = time.monotonic()
    result = subprocess.run(
        argv,
        cwd=cwd,
        timeout=timeout,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    end = time.monotonic()
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "seconds": end - start,
    }
