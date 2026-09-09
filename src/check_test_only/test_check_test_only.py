import pytest

from check_test_only.check_test_only import check_test_only

TEST = "from {n}.{n} import {n}\n\n\ndef test_adds():\n    assert {n}(1) == 2\n"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "src").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _folder(root, n, text=TEST):
    d = root / "src" / n
    d.mkdir()
    (d / f"test_{n}.py").write_text(text.format(n=n))


def test_clean_without_code(repo):
    _folder(repo, "clean")
    assert check_test_only("clean", {"cases": ["adds"]}) == []


def test_missing_file(repo):
    (repo / "src" / "gone").mkdir()
    assert check_test_only("gone", {}) == ["test_file_missing"]


def test_case_rules(repo):
    _folder(repo, "cased")
    assert check_test_only("cased", {"cases": ["other"]}) == [
        "case_missing",
        "case_extra",
    ]
    assert check_test_only("cased", {}) == []


def test_lint_named(repo):
    _folder(repo, "bad", text="import os\n\n\ndef test_adds():\n    assert True\n")
    assert "lint_findings" in check_test_only("bad", {"cases": ["adds"]})


def test_file_outside_folder_named(repo):
    """A test job that writes outside its folder fails, as a code job does."""
    _folder(repo, "tidy")
    changed = ["src/tidy/test_tidy.py", "src/second/leftover.txt"]
    assert "file_outside_folder" in check_test_only("tidy", {"changed": changed})
    inside = check_test_only("tidy", {"changed": changed[:1]})
    assert "file_outside_folder" not in inside


def test_markdown_and_third_file_named(repo):
    _folder(repo, "docs")
    changed = ["src/docs/test_docs.py", "roles/builder/SKILL.md"]
    assert "markdown_touched" in check_test_only("docs", {"changed": changed})
    files = ["docs.py", "test_docs.py", "__main__.py"]
    assert "too_many_files" in check_test_only("docs", {"files": files})
    assert "too_many_files" not in check_test_only("docs", {"files": files[:2]})


def test_suppression_comment_named(repo):
    text = "def test_adds():  # noqa\n    assert True\n"
    _folder(repo, "quiet", text=text)
    assert "suppressed_lint" in check_test_only("quiet", {"cases": ["adds"]})
