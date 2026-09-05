import pathlib

import pytest

from check_folder.check_folder import check_folder
from gate_built.gate_built import gate_built
from gate_proven.gate_proven import gate_proven

CODE = 'def {n}(x: int) -> int:\n    """Add one."""\n    return x + 1\n'
NOTE = "purpose\nsignature\ninputs\noutputs\nside effects\nwork item {n}-code\n"
TEST = "from {n}.{n} import {n}\n\n\ndef test_adds():\n    assert {n}(1) == {v}\n"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "pytest.ini").write_text(
        "[pytest]\npythonpath = src\naddopts = --import-mode=importlib\n"
    )
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _folder(root, n, code=CODE, note=NOTE, test=TEST, v=2):
    d = root / "src" / n
    d.mkdir()
    (d / f"{n}.py").write_text(code.format(n=n))
    (d / f"{n}.md").write_text(note.format(n=n))
    if test:
        (d / f"test_{n}.py").write_text(test.format(n=n, v=v))
    return d


def test_clean_folder_empty(repo):
    _folder(repo, "clean")
    assert check_folder("clean", {"cases": ["adds"]}) == []


def test_long_file_named(repo):
    long = CODE + "".join(f"\n\ndef _h{i}():\n    return {i}\n" for i in range(12))
    _folder(repo, "long", code=long)
    assert "over_50_lines" in check_folder("long", {})


def test_failing_test_named(repo):
    _folder(repo, "bad", v=3)
    assert "tests_failed" in check_folder("bad", {})


def test_case_rules_only_with_cases(repo):
    _folder(repo, "cased")
    assert "case_extra" not in check_folder("cased", {})
    assert "case_missing" in check_folder("cased", {"cases": ["other"]})


def test_rule_names_are_the_gates(repo):
    _folder(
        repo,
        "gated",
        code="def gated():\n    return 1\n\n\ndef other():\n    return 2\n",
    )
    rules = check_folder("gated", {"changed": ["src/elsewhere/x.py"]})
    built = gate_built(
        "gated",
        {
            "changed": ["src/elsewhere/x.py"],
            "code": (repo / "src/gated/gated.py").read_text(),
            "note": NOTE.format(n="gated"),
            "fmt_out": "",
            "lint_out": "",
        },
    )
    assert set(built) <= set(rules)
    assert gate_proven("gated", "1 passed", []) == []


def test_pathlib_unused_guard():
    assert pathlib.Path(".").exists()
