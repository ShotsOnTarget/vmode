purpose: create a function's code and test jobs as siblings, tests first
signature: create_pair(story_id: str, function_name: str, owner: str) -> dict
inputs: the Story id, the function name, the owner role
outputs: {'code': id, 'test': id}; code needs test, test checks code
side effects: two items and two links in the record
work item id: 0006-2-create_pair-code
