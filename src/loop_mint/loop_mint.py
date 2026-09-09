from record_create_item.record_create_item import record_create_item
from record_graph.record_graph import record_graph
from record_set_checklist.record_set_checklist import record_set_checklist
from record_set_sheet.record_set_sheet import record_set_sheet


def loop_mint(intent_id: str) -> str:
    """Mint a waiting loop-drive Story under an Intent.

    Inputs: intent_id, the id of an Intent in the record; when no item
    has that id, one is created first and used instead. Outputs: the id
    of a new Story under that Intent. Side effects: creates the Story
    with a five-item checklist, a sheet and a Verification linked to it,
    through the record, leaving it in state waiting with no labels.
    """
    if intent_id not in record_graph():
        intent_id = record_create_item("intent", "loop drive intent", "board")["id"]
    story_id = record_create_item("story", "loop drive", "architect", intent_id)["id"]
    record_set_checklist(
        story_id,
        [
            "an intent is read from the record [testing]",
            "a missing intent is created first [testing]",
            "the story hangs under the intent [testing]",
            "the story carries its five-item checklist [testing]",
            "the story is checked by its verification [testing]",
        ],
    )
    record_set_sheet(story_id, "loop drive pipeline")
    record_create_item("verification", "verify loop drive", "architect", story_id)
    return story_id
