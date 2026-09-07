import os
import subprocess

from check_test_only.check_test_only import check_test_only
from gate_built.gate_built import gate_built
from gate_proven.gate_proven import gate_proven


def _read(path: str) -> str:
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


def _run(cmd: list[str], repo: str, both: bool = False) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=repo)
    return proc.stdout + proc.stderr if both else proc.stdout


def check_folder(folder: str, options: dict) -> list[str]:
    """The one check: shape, format, lint and tests for src/<folder>.

    options: changed (paths changed in the working tree, default []), cases
    (test names the sheet requires; None skips the case rules), repo (the
    tree to check, default '.'). Returns the failed rule names exactly as
    the Built and Proven gates name them; [] when clean. Tests run whenever
    a test file exists, so a code job is checked against its tests too. A
    test job always gets the test-only gate: its own file's shape, format,
    lint and case names, and no pytest run. The pair's tests are run at the
    code job's gate, which comes after it. Running them at the test job's
    gate deadlocks a change pair, whose new cases describe behaviour the
    unchanged code does not have yet (Intent 0009).
    """
    repo = options.get("repo", ".")
    src, base = f"src/{folder}", os.path.join(repo, "src", folder, folder)
    if options.get("kind") == "test":
        return check_test_only(folder, options)
    inputs = {
        "changed": options.get("changed", []),
        "code": _read(base + ".py"),
        "fmt_out": _run(["ruff", "format", "--check", "--diff", src], repo, True),
        "lint_out": _run(["ruff", "check", src, "--output-format", "concise"], repo),
    }
    rules = gate_built(folder, inputs)
    if not os.path.exists(os.path.join(repo, src, f"test_{folder}.py")):
        return rules
    out = _run(["python", "-m", "pytest", src, "-q", "-rA"], repo, True)
    cases = options.get("cases")
    proven = gate_proven(folder, out, cases if cases is not None else [])
    if cases is None:
        proven = [r for r in proven if r == "tests_failed"]
    return rules + proven
