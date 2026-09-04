import pytest

from record_list_kind.record_list_kind import record_list_kind
from record_run.record_run import record_run


def test_filters_by_kind(bd_repo):
    record_run(["create", "intent one", "-l", "kind:intent", "-t", "epic"])
    story_a = record_run(["create", "story a", "-l", "kind:story", "-t", "task"])
    story_b = record_run(["create", "story b", "-l", "kind:story", "-t", "task"])

    result = record_list_kind("story")

    assert len(result) == 2
    ids = {item["id"] for item in result}
    assert ids == {story_a["id"], story_b["id"]}
    for item in result:
        assert item["kind"] == "story"


def test_includes_closed(bd_repo):
    story = record_run(["create", "story c", "-l", "kind:story", "-t", "task"])
    record_run(["update", story["id"], "-s", "closed", "--add-label", "state:done"])

    result = record_list_kind("story")

    ids = {item["id"] for item in result}
    assert story["id"] in ids


def test_empty_kind_returns_empty(bd_repo):
    assert record_list_kind("validation") == []


def test_bad_kind_rejected(bd_repo):
    with pytest.raises(ValueError):
        record_list_kind("bug")
