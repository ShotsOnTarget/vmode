import subprocess
import time


def harness_run(argv: list[str], cwd: str, timeout: int = 1800) -> dict:
    """Run one harness command and capture its result.

    argv: the full command line, executable first. cwd: the directory the
    child runs in. timeout: whole seconds the child is allowed before its
    whole process tree is killed; default 1800. Returns a dict with stdout
    (str), stderr (str), returncode (int, as-is), and seconds (float,
    wall-clock time around the child run). A child that outlives timeout has
    its whole process tree killed, without waiting for any pipe to close;
    the result then carries what the child printed so far, returncode -1,
    and a stderr that starts 'timed out after N seconds', so a caller can
    write the transcript of a run that hung and say why it was released.
    """
    start = time.monotonic()
    proc = subprocess.Popen(
        argv,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
        )
        stdout, stderr = proc.communicate()
        stderr = f"timed out after {timeout} seconds\n" + stderr
        returncode = -1
    else:
        returncode = proc.returncode
    end = time.monotonic()
    return {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "seconds": end - start,
    }
