from log_append.log_append import log_append
from record_graph.record_graph import record_graph
from record_run.record_run import record_run


def _create(title, *extra):
    created = record_run(["create", title, "--no-inherit-labels", *extra])
    return created[0]["id"] if isinstance(created, list) else created["id"]


def test_keys_are_all_ids(bd_repo):
    intent = _create("intent1", "-t", "epic")
    story = _create("story1", "--parent", intent)
    graph = record_graph()
    assert set(graph.keys()) == {intent, story}


def test_kind_and_state_from_labels(bd_repo):
    story = _create("story1", "-l", "kind:story,state:waiting,owner:architect")
    graph = record_graph()
    assert graph[story]["kind"] == "story"
    assert graph[story]["state"] == "waiting"
    assert graph[story]["owner"] == "architect"
    assert graph[story]["claimed_by"] == ""


def test_parent_and_checks(bd_repo):
    intent = _create("intent1", "-t", "epic")
    story = _create("story1", "--parent", intent)
    verification = _create("verification1")
    record_run(["dep", "add", verification, story, "-t", "validates"])
    graph = record_graph()
    assert graph[story]["parent"] == intent
    assert graph[verification]["checks"] == [story]


def test_parent_from_validates(bd_repo):
    story = _create("story1")
    verification = _create("verification1")
    record_run(["dep", "add", verification, story, "-t", "validates"])
    graph = record_graph()
    assert graph[verification]["parent"] == story


def test_needs_from_blocks(bd_repo):
    intent = _create("intent1", "-t", "epic")
    story_a = _create("storyA", "--parent", intent)
    story_b = _create("storyB", "--parent", intent)
    record_run(["dep", "add", story_b, "--blocked-by", story_a])
    graph = record_graph()
    assert graph[story_b]["needs"] == [story_a]


def test_events_not_in_graph(bd_repo):
    item = _create("item1")
    event_id = log_append(
        {
            "item": item,
            "gate": "Built",
            "rule": "rule1",
            "inputs": {},
            "state": "ok",
            "tokens": 1,
            "seconds": 0.1,
            "actor": "builder",
        }
    )
    graph = record_graph()
    assert event_id not in graph
    assert item in graph


def test_test_keeps_its_parent(bd_repo):
    story = _create("story1")
    code = _create("code1", "--parent", story)
    test = _create("test1", "--parent", story)
    record_run(["label", "add", test, "kind:test"])
    record_run(["dep", "add", test, code, "-t", "validates"])
    graph = record_graph()
    assert graph[test]["parent"] == story
    assert graph[test]["checks"] == [code]
