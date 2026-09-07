import os
import subprocess
import sys
import time

import pytest

from harness_run.harness_run import harness_run

_TREE_CHILD = (
    "import subprocess, sys, time\n"
    "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
    "open(sys.argv[1], 'w').write(str(p.pid))\n"
    "time.sleep(60)\n"
)


def _pid_running(pid: str) -> bool:
    out = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True
    ).stdout
    return pid in out


def test_returns_the_four_keys(tmp_path):
    result = harness_run(
        [
            sys.executable,
            "-c",
            "import sys; print('hi'); print('err', file=sys.stderr)",
        ],
        str(tmp_path),
    )
    assert set(result.keys()) == {"stdout", "stderr", "returncode", "seconds"}


def test_stdout_and_stderr_come_back_separately(tmp_path):
    result = harness_run(
        [
            sys.executable,
            "-c",
            "import sys; print('hi'); print('err', file=sys.stderr)",
        ],
        str(tmp_path),
    )
    assert "hi" in result["stdout"]
    assert "err" in result["stderr"]


def test_nonzero_exit_is_returned_not_raised(tmp_path):
    result = harness_run(
        [sys.executable, "-c", "import sys; sys.exit(3)"], str(tmp_path)
    )
    assert result["returncode"] == 3


def test_zero_exit_is_returned(tmp_path):
    result = harness_run([sys.executable, "-c", "pass"], str(tmp_path))
    assert result["returncode"] == 0


def test_seconds_covers_the_child(tmp_path):
    result = harness_run(
        [sys.executable, "-c", "import time; time.sleep(0.5)"], str(tmp_path)
    )
    assert isinstance(result["seconds"], float)
    assert result["seconds"] >= 0.4


def test_runs_in_the_given_cwd(tmp_path):
    caller_cwd = os.getcwd()
    result = harness_run(
        [sys.executable, "-c", "import os; print(os.getcwd())"], str(tmp_path)
    )
    printed = result["stdout"].strip()
    assert os.path.samefile(printed, str(tmp_path))
    assert not os.path.samefile(printed, caller_cwd)


def test_timeout_reaches_the_caller(tmp_path):
    with pytest.raises(subprocess.TimeoutExpired):
        harness_run(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            str(tmp_path),
            timeout=1,
        )


def test_undecodable_bytes_do_not_break_it(tmp_path):
    result = harness_run(
        [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write(b'\\xff\\xfe\\x00')",
        ],
        str(tmp_path),
    )
    assert isinstance(result["stdout"], str)


def test_timeout_fires_while_a_grandchild_holds_the_pipes(tmp_path):
    pid_file = tmp_path / "grandchild_pid.txt"
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        harness_run(
            [sys.executable, "-c", _TREE_CHILD, str(pid_file)],
            str(tmp_path),
            timeout=2,
        )
    elapsed = time.monotonic() - start
    assert elapsed <= 2 + 5


def test_timeout_ends_the_whole_process_tree(tmp_path):
    pid_file = tmp_path / "grandchild_pid.txt"
    with pytest.raises(subprocess.TimeoutExpired):
        harness_run(
            [sys.executable, "-c", _TREE_CHILD, str(pid_file)],
            str(tmp_path),
            timeout=2,
        )
    grandchild_pid = pid_file.read_text().strip()
    assert not _pid_running(grandchild_pid)
