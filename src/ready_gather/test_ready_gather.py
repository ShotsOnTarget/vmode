import pytest

from ready_gather.ready_gather import ready_gather
from record_run.record_run import record_run


def _create(title, labels, parent=None, sheet=None):
    args = ["create", title, "-t", "task", "--no-inherit-labels", "-l", labels]
    if parent:
        args += ["--parent", parent]
    if sheet is not None:
        args += ["-d", sheet]
    return record_run(args)["id"]


def _root(fake_bd):
    (fake_bd / "src").mkdir(parents=True, exist_ok=True)
    return str(fake_bd)


def test_sheets_for_every_job(fake_bd):
    story = _create("S", "kind:story,state:in_progress")
    code = _create("C", "kind:code,state:waiting", parent=story, sheet="code-sheet")
    test = _create("T", "kind:test,state:waiting", parent=story)
    result = ready_gather(story, _root(fake_bd))
    assert result["jobs"] == sorted([code, test])
    assert result["sheets"] == {code: "code-sheet", test: ""}


def test_checklist_parsed(fake_bd):
    story = _create("S", "kind:story,state:in_progress")
    record_run(["update", story, "--acceptance", "1. a [testing] 2. b [looking]"])
    result = ready_gather(story, _root(fake_bd))
    assert result["checklist"] == ["a [testing]", "b [looking]"]


def test_usage_from_last_comment(fake_bd):
    story = _create("S", "kind:story,state:in_progress")
    record_run(["comment", story, 'usage: {"n": 1}'])
    record_run(["comment", story, 'usage: {"n": 2}'])
    result = ready_gather(story, _root(fake_bd))
    assert result["usage"] == {"n": 2}


def test_usage_empty_without_comment(fake_bd):
    story = _create("S", "kind:story,state:in_progress")
    result = ready_gather(story, _root(fake_bd))
    assert result["usage"] == {}


def test_existing_from_map(fake_bd):
    story = _create("S", "kind:story,state:in_progress")
    folder = fake_bd / "src" / "f"
    folder.mkdir(parents=True)
    (folder / "f.py").write_text("def f():\n    pass\n")
    result = ready_gather(story, str(fake_bd))
    assert result["existing"] == ["f"]


def test_not_a_story_raises(fake_bd):
    code = _create("C", "kind:code,state:waiting")
    with pytest.raises(ValueError):
        ready_gather(code, _root(fake_bd))


def test_existing_tests_by_function(fake_bd):
    story = _create("S", "kind:story,state:in_progress")
    folder = fake_bd / "src" / "f"
    folder.mkdir(parents=True)
    (folder / "f.py").write_text("def f():\n    pass\n")
    (folder / "test_f.py").write_text(
        "def test_b():\n    pass\n\n\ndef test_a():\n    pass\n"
    )
    result = ready_gather(story, str(fake_bd))
    assert result["existing"] == ["f"]
    assert result["existing_tests"] == {"f": ["test_b", "test_a"]}
