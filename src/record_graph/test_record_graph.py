from record_run.record_run import record_run
from record_graph.record_graph import record_graph


def _id(created):
    return created[0]["id"] if isinstance(created, list) else created["id"]


def test_keys_are_all_ids(bd_repo):
    intent = _id(record_run(["create", "intent1", "-t", "epic", "-a", "me", "--no-inherit-labels"]))
    story = _id(record_run(["create", "story1", "-a", "me", "--no-inherit-labels", "--parent", intent]))
    graph = record_graph()
    assert set(graph.keys()) == {intent, story}


def test_kind_and_state_from_labels(bd_repo):
    story = _id(record_run(["create", "story1", "-a", "me", "--no-inherit-labels",
                             "-l", "kind:story,state:waiting"]))
    graph = record_graph()
    assert graph[story]["kind"] == "story"
    assert graph[story]["state"] == "waiting"


def test_parent_and_checks(bd_repo):
    intent = _id(record_run(["create", "intent1", "-t", "epic", "-a", "me", "--no-inherit-labels"]))
    story = _id(record_run(["create", "story1", "-a", "me", "--no-inherit-labels", "--parent", intent]))
    verification = _id(record_run(["create", "verification1", "-a", "me", "--no-inherit-labels"]))
    record_run(["dep", "add", verification, story, "-t", "validates"])
    graph = record_graph()
    assert graph[story]["parent"] == intent
    assert graph[verification]["checks"] == [story]


def test_parent_from_validates(bd_repo):
    story = _id(record_run(["create", "story1", "-a", "me", "--no-inherit-labels"]))
    verification = _id(record_run(["create", "verification1", "-a", "me", "--no-inherit-labels"]))
    record_run(["dep", "add", verification, story, "-t", "validates"])
    graph = record_graph()
    assert graph[verification]["parent"] == story


def test_needs_from_blocks(bd_repo):
    intent = _id(record_run(["create", "intent1", "-t", "epic", "-a", "me", "--no-inherit-labels"]))
    story_a = _id(record_run(["create", "storyA", "-a", "me", "--no-inherit-labels", "--parent", intent]))
    story_b = _id(record_run(["create", "storyB", "-a", "me", "--no-inherit-labels", "--parent", intent]))
    record_run(["dep", "add", story_b, "--blocked-by", story_a])
    graph = record_graph()
    assert graph[story_b]["needs"] == [story_a]
