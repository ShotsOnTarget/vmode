from record_run.record_run import record_run, RecordError


def record_add_note(item_id: str, text: str) -> dict:
    if not text:
        raise ValueError("text must not be empty")
    result = record_run(['comment', item_id, text])
    return {'id': item_id, 'note_id': result['id']}
