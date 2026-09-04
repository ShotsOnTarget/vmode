Purpose: claim a ready, unassigned item in the record for an actor, atomically.
Signature: claim_item(item_id: str, actor: str) -> dict
Inputs: item_id (item in state ready, unassigned), actor (unique puller name, e.g. builder-1)
Outputs: {'id': item_id, 'claimed_by': actor, 'state': 'in_progress'}
Side effects: runs bd update --claim --actor <actor>, then sets state:in_progress label on the item
Work item id: 0003-2-claim_item-code
