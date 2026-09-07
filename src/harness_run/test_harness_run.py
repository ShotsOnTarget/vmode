import os
import subprocess
import sys

import pytest
from harness_run.harness_run import harness_run


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
