purpose: find the code and test items belonging to a story, and whether it has an intent ancestor
signature: story_jobs(story_id: str, graph: dict) -> dict
inputs: story_id in graph; graph is the dict documented in work/sheets/record_graph-code.md
outputs: {'has_intent': bool, 'code': sorted ids of kind code whose parent is story_id, 'tests': dict code_id -> sorted ids of kind test whose checks contains that code_id}
side effects: none
work item id 0003-1-story_jobs-code
