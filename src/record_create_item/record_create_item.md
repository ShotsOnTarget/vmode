purpose: Create a new work item record via bd, in the waiting state.
signature: record_create_item(kind: str, title: str, owner: str, parent: str | None = None) -> dict
inputs: kind (one of intent, story, code, test, verification, validation, proposal), title (non-empty), owner (non-empty), parent (existing id, required unless kind is intent)
outputs: {'id': str, 'kind': str, 'title': str, 'owner': str, 'parent': str | None, 'state': 'waiting'}
side effects: invokes the external `bd` command to create a record
work item id: 0001-1-record_create_item-code
