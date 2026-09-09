import pytest
from scripted_engineer.scripted_engineer import scripted_engineer

from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item
from sheet_fields.sheet_fields import sheet_fields


def _story():
    intent = record_create_item("intent", "I", "board")
    return record_create_item("story", "S", "architect", intent["id"])["id"]


def _item(story_id, recipe):
    return {
        "id": story_id,
        "kind": "story",
        "state": "waiting",
        "labels": ["kind:story", "state:waiting"],
        "last_gate": "",
        "recipe": recipe,
    }


def _code_jobs(story_id):
    graph = record_graph()
    return {
        graph[j]["title"]: j
        for j in graph
        if graph[j]["parent"] == story_id and graph[j]["kind"] == "code"
    }


def test_cuts_two_recipe_functions(fake_bd):
    story = _story()
    recipe = {"functions": ["frob", "qux"]}

    usage = scripted_engineer(_item(story, recipe), "cut")

    graph = record_graph()
    jobs = {
        j
        for j in graph
        if graph[j]["parent"] == story and graph[j]["kind"] in ("code", "test")
    }
    titles = {graph[j]["title"] for j in jobs}
    assert titles == {"frob code", "frob test", "qux code", "qux test"}
    for job in jobs:
        assert record_show_item(job)["sheet"] != ""
    row = record_run(["show", story])
    row = row[0] if isinstance(row, list) else row
    assert "cut" in row["labels"]
    comments = row.get("comments", [])
    assert comments and "cut" in comments[-1]["text"].lower()
    assert set(usage) == {"tokens", "seconds", "harness", "model"}


def test_omits_change_for_planted_fault(fake_bd):
    story = _story()
    recipe = {"functions": ["frob", "qux"], "faults": {"qux": "no_change"}}

    scripted_engineer(_item(story, recipe), "cut")

    code_jobs = _code_jobs(story)
    clean = sheet_fields(record_show_item(code_jobs["frob code"])["sheet"])
    faulted = sheet_fields(record_show_item(code_jobs["qux code"])["sheet"])
    assert "change" in clean
    assert "change" not in faulted
    assert set(faulted) - set(clean) == set()
    assert set(clean) - set(faulted) == {"change"}


def test_rejects_unknown_fault_before_record_changes(fake_bd):
    story = _story()
    recipe = {"functions": ["frob"], "faults": {"frob": "bogus"}}
    before = record_graph()

    with pytest.raises(ValueError):
        scripted_engineer(_item(story, recipe), "cut")

    assert record_graph() == before
