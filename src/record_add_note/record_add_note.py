from record_run.record_run import record_run


def record_add_note(item_id: str, text: str) -> dict:
    """Add a note (comment) to an existing record item."""
    if not text:
        raise ValueError("text must not be empty")
    result = record_run(["comment", item_id, text])
    return {"id": item_id, "note_id": result["id"]}
