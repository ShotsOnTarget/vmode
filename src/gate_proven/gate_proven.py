import re


def _tests_failed(lines: list[str]) -> bool:
    failed = any(
        " FAILED " in line or line.startswith("FAILED ") or " ERROR " in line
        for line in lines
    )
    summary = ""
    for line in reversed(lines):
        if line.strip():
            summary = line
            break
    return failed or "passed" not in summary


def _case_missing(lines: list[str], cases: list[str]) -> bool:
    return any(not any(f"test_{case}" in line for line in lines) for case in cases)


def _case_extra(pytest_output: str, cases: list[str]) -> bool:
    names = re.findall(r"::(test_\w+)", pytest_output)
    return any(name[len("test_") :] not in cases for name in names)


def gate_proven(job_id: str, pytest_output: str, cases: list[str]) -> list[str]:
    rules = []
    lines = pytest_output.splitlines()
    if _tests_failed(lines):
        rules.append("tests_failed")
    if _case_missing(lines, cases):
        rules.append("case_missing")
    if _case_extra(pytest_output, cases):
        rules.append("case_extra")
    return rules
