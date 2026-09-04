purpose: add a note (comment) to an existing record item
signature: record_add_note(item_id: str, text: str) -> dict
inputs: item_id existing; text non-empty
outputs: {'id': item_id, 'note_id': str} where note_id comes from the comment's 'id' field
side effects: invokes record_run(['comment', item_id, text]), which calls the external record command
work item id: 0001-4-record_add_note-code
