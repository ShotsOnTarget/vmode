import os
import re
import subprocess

_SUPPRESS = re.compile(r"#\s*(noqa|fmt:\s*(off|skip)|type:\s*ignore|ruff:\s*noqa)")


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


def _path_rules(src: str, changed: list[str], files: list[str] | None) -> list[str]:
    """The same three path rules gate_built applies: a test job may not
    touch anything outside its folder either (a second folder passed on
    2026-09-09), nor documentation, nor leave a third file in the folder."""
    folder = src + "/"
    held = (
        set(files)
        if files is not None
        else {p for p in changed if p.startswith(folder)}
    )
    rules = []
    if any(not p.startswith(folder) for p in changed):
        rules.append("file_outside_folder")
    if any(p.endswith(".md") for p in changed):
        rules.append("markdown_touched")
    if len(held) > 2:
        rules.append("too_many_files")
    return rules


def _case_rules(path: str, cases: list[str] | None) -> list[str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    rules = ["suppressed_lint"] if _SUPPRESS.search(text) else []
    if cases is None:
        return rules
    names = re.findall(r"^def test_(\w+)", text, re.M)
    if any(c not in names for c in cases):
        rules.append("case_missing")
    if any(n not in cases for n in names):
        rules.append("case_extra")
    return rules


def check_test_only(folder: str, options: dict) -> list[str]:
    """The gate for a test job whose code does not exist yet (tests first).

    Checks what can be checked without code: only the folder changed and it
    holds at most two files (changed, files), the folder is formatted and
    lint-clean with no suppression comment, the test file exists, and its
    test functions match the sheet's cases (case_missing, case_extra) when
    options carries cases. The tests themselves run later, at the code
    job's gate. options: changed, files, cases, repo. Rule names are the
    gates' own.
    """
    repo = options.get("repo", ".")
    src = f"src/{folder}"
    path = os.path.join(repo, src, f"test_{folder}.py")
    if not os.path.exists(path):
        return ["test_file_missing"]
    rules = _path_rules(src, options.get("changed", []), options.get("files"))
    return rules + _tool_rules(src, repo) + _case_rules(path, options.get("cases"))
