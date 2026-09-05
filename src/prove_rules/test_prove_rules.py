import pytest

from prove_rules.prove_rules import prove_rules

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


def _folder(root, n, v=2):
    d = root / "src" / n
    d.mkdir()
    (d / f"{n}.py").write_text(CODE.format(n=n))
    (d / f"{n}.md").write_text(NOTE.format(n=n))
    (d / f"test_{n}.py").write_text(TEST.format(n=n, v=v))


def _gathered(n, kind, cases):
    return {"folder": n, "kind": kind, "changed": [f"src/{n}/{n}.py"], "cases": cases}


def test_clean_code_empty(repo):
    _folder(repo, "clean")
    assert prove_rules(_gathered("clean", "code", [])) == []


def test_code_skips_case_rules(repo):
    _folder(repo, "coded")
    assert prove_rules(_gathered("coded", "code", ["other"])) == []


def test_test_runs_case_rules(repo):
    _folder(repo, "tested")
    assert "case_missing" in prove_rules(_gathered("tested", "test", ["other"]))


def test_code_proven_against_tests(repo):
    _folder(repo, "broken", v=3)
    assert "tests_failed" in prove_rules(_gathered("broken", "code", []))
