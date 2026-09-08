from record_create_item.record_create_item import record_create_item
from record_set_checklist.record_set_checklist import record_set_checklist
from record_set_sheet.record_set_sheet import record_set_sheet


def smoke_story(intent_id: str, target: int) -> dict:
    """Mint a waiting smoke Story asking for one pipeline run count.

    Inputs: intent_id, the standing Intent that owns the Story; target,
    the pipeline run count the Story requests. Outputs: a dict with
    the fresh Story id under 'story_id' and the target under 'target'.
    Side effects: creates a story under intent_id and writes its
    checklist and sheet through the record.
    """
    story_id = record_create_item("story", "smoke run", "architect", intent_id)["id"]
    record_set_checklist(story_id, [f"pipeline run count is {target} [testing]"])
    record_set_sheet(story_id, f"smoke run for target {target}: pipeline_run_count")
    return {"story_id": story_id, "target": target}
