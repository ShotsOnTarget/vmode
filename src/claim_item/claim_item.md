Purpose: claim a ready item in the record for an owner, atomically.
Signature: claim_item(item_id: str, owner: str) -> dict
Inputs: item_id (item in state ready), owner (claimant name)
Outputs: {'id': item_id, 'owner': owner, 'state': 'in_progress'}
Side effects: runs bd update --claim, then sets assignee and state:in_progress label on the item
Work item id: 0003-2-claim_item-code
