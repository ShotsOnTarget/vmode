purpose: set the owner of an existing record item
signature: record_set_owner(item_id: str, owner: str) -> dict
inputs: item_id existing; owner non-empty
outputs: {'id': item_id, 'owner': owner}
side effects: via record_run, removes every label starting 'owner:' then adds 'owner:<owner>'; never touches the assignee
work item id: 0001-4-record_set_owner-code
