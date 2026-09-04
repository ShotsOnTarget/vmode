purpose: set the owner of an existing record item
signature: record_set_owner(item_id: str, owner: str) -> dict
inputs: item_id existing; owner non-empty
outputs: {'id': item_id, 'owner': owner}
side effects: runs `bd update <item_id> -a <owner>` via record_run
work item id: 0001-4-record_set_owner-code
