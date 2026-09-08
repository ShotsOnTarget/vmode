from record_add_link.record_add_link import record_add_link
from record_create_item.record_create_item import record_create_item
from record_set_checklist.record_set_checklist import record_set_checklist
from record_set_sheet.record_set_sheet import record_set_sheet


def smoke_story(intent_id: str, target: int) -> dict:
    """Mint a waiting smoke Story asking for one pipeline run count.

    Inputs: intent_id, the standing Intent that owns the Story; target,
    the pipeline run count the Story requests. Outputs: a dict with the
    fresh Story id under 'story_id', the target under 'target', and the
    Verification that checks the Story under 'verification_id'.
    Side effects: creates the Story under intent_id with its checklist
    and sheet, and a Verification linked to it, through the record. The
    Verification is not optional: the Ready gate refuses a Story that
    nothing checks, so a Story minted without one can never be built.
    """
    story_id = record_create_item("story", "smoke run", "architect", intent_id)["id"]
    record_set_checklist(story_id, [f"pipeline run count is {target} [testing]"])
    record_set_sheet(story_id, f"smoke run for target {target}: pipeline_run_count")
    checker = record_create_item(
        "verification", "verify smoke run", "architect", story_id
    )
    record_add_link("checks", checker["id"], story_id)
    return {"story_id": story_id, "target": target, "verification_id": checker["id"]}
