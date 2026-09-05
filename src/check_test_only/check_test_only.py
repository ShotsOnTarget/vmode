import os
import re
import subprocess


def _run(cmd: list[str], repo: str) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=repo)
    return proc.stdout + proc.stderr


def _tool_rules(src: str, repo: str) -> list[str]:
    fmt = _run(["ruff", "format", "--check", "--diff", src], repo)
    lint = _run(["ruff", "check", src, "--output-format", "concise"], repo)
    rules = ["not_formatted"] if "---" in fmt or "would reformat" in fmt else []
    if lint and not lint.startswith("All checks passed"):
        rules.append("lint_findings")
    return rules


def _case_rules(path: str, cases: list[str] | None) -> list[str]:
    if cases is None:
        return []
    with open(path, encoding="utf-8") as f:
        names = re.findall(r"^def test_(\w+)", f.read(), re.M)
    missing = ["case_missing"] if any(c not in names for c in cases) else []
    extra = ["case_extra"] if any(n not in cases for n in names) else []
    return missing + extra


def check_test_only(folder: str, options: dict) -> list[str]:
    """The gate for a test job whose code does not exist yet (tests first).

    Checks what can be checked without code: the folder is formatted and
    lint-clean, the test file exists, and its test functions match the
    sheet's cases (case_missing, case_extra) when options carries cases.
    The tests themselves run later, at the code job's gate. options: cases,
    repo. Rule names are the gates' own.
    """
    repo = options.get("repo", ".")
    src = f"src/{folder}"
    path = os.path.join(repo, src, f"test_{folder}.py")
    if not os.path.exists(path):
        return ["test_file_missing"]
    return _tool_rules(src, repo) + _case_rules(path, options.get("cases"))
