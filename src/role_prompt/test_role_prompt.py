from role_prompt.role_prompt import role_prompt

from builder_prompt.builder_prompt import builder_prompt


def test_job_kinds_delegate():
    for kind in ("code", "test"):
        item = {"id": "vm-x", "kind": kind}
        assert role_prompt(item, "builder", "R") == builder_prompt(item, "builder", "R")


def test_story_prompt_names_role_and_item():
    item = {"id": "vm-9", "kind": "story"}
    prompt = role_prompt(item, "engineer", "C:/work")
    assert "You are the engineer" in prompt
    assert "C:/work" in prompt
    assert "roles/engineer/SKILL.md" in prompt
    assert "vm-9" in prompt


def test_story_prompt_has_no_test_words():
    prompt = role_prompt({"id": "vm-9", "kind": "story"}, "engineer", "C:/work")
    assert "test" not in prompt
    assert "tests" not in prompt
    assert "code file" not in prompt


def test_story_prompt_exact():
    prompt = role_prompt({"id": "vm-1", "kind": "story"}, "engineer", "R")
    assert prompt == (
        "You are the engineer. Working directory: R. "
        "Read roles/engineer/SKILL.md and follow it exactly. "
        "Your work item id is vm-1. "
        "Fetch it from the record with the work-record skill "
        "(roles/work-record/SKILL.md). Do only that item. "
        "When you are done, say what you did in one paragraph and nothing else."
    )
