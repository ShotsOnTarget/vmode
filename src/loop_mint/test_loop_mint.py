from loop_mint.loop_mint import loop_mint

from checklist_items.checklist_items import checklist_items
from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_run.record_run import record_run
from record_show_item.record_show_item import record_show_item


def _intent_id():
    return record_create_item("intent", "i", "board")["id"]


def _checklist(story_id):
    row = record_run(["show", story_id])[0]
    return checklist_items(row.get("acceptance_criteria", ""))


def test_story_hangs_under_the_given_intent(fake_bd):
    intent_id = _intent_id()
    story_id = loop_mint(intent_id)
    shown = record_show_item(story_id)
    assert shown["kind"] == "story"
    assert shown["state"] == "waiting"
    assert shown["parent"] == intent_id


def test_story_has_checklist_sheet_and_verification(fake_bd):
    story_id = loop_mint(_intent_id())
    shown = record_show_item(story_id)
    assert shown["sheet"] == "loop drive pipeline"
    assert len(_checklist(story_id)) == 5
    verifications = [
        item
        for item in record_graph().values()
        if item["kind"] == "verification" and item["parent"] == story_id
    ]
    assert len(verifications) == 1


def test_missing_intent_is_created(fake_bd):
    story_id = loop_mint("vm-does-not-exist")
    shown = record_show_item(story_id)
    assert shown["kind"] == "story"
    parent = shown["parent"]
    graph = record_graph()
    assert parent in graph
    assert graph[parent]["kind"] == "intent"
