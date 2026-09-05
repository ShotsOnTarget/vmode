from record_add_link.record_add_link import record_add_link
from record_create_item.record_create_item import record_create_item


def create_pair(story_id: str, function_name: str, owner: str) -> dict:
    """Create the code and test jobs for one function under a Story.

    Both hang under the Story as siblings. The test checks the code
    (validates link) and the code needs the test first (needs link), so the
    code job cannot be pulled until the test job is done: tests first.
    Returns {'code': id, 'test': id}.
    """
    if not function_name or " " in function_name:
        raise ValueError(f"bad function name: {function_name!r}")
    code = record_create_item("code", f"{function_name} code", owner, story_id)
    test = record_create_item("test", f"{function_name} test", owner, code["id"])
    record_add_link("needs_first", code["id"], test["id"])
    return {"code": code["id"], "test": test["id"]}
