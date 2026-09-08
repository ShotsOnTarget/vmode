def builder_prompt(item: dict, role: str, root: str) -> str:
    """The one prompt a puller hands a harness for one item.

    Names the role, the working directory, the item id, and how to fetch the
    sheet through the work-record skill. A test job is told to write tests
    from the sheet and never touch the code file; a code job is told not to
    write tests. When the item carries last_gate (what the last gate or
    failed run said, see last_gate), the prompt ends with it, so a retry
    starts from the rule that failed. The same text on every harness, so
    runs are comparable.
    """
    kind_note = (
        "You write your tests from the sheet; you never create or edit the code file. "
        if item["kind"] == "test"
        else "Do not write tests. "
    )
    return (
        f"You are the {role}. Working directory: {root}. "
        f"Read roles/{role}/SKILL.md and follow it exactly. "
        f"Your work item id is {item['id']}. "
        "Fetch it from the record with the work-record skill "
        "(roles/work-record/SKILL.md). "
        "Do only that item. "
        f"{kind_note}"
        "Report in roles/shared/report-format.md and nothing else." + _last_gate(item)
    )


def _last_gate(item: dict) -> str:
    said = item.get("last_gate")
    if not said:
        return ""
    return f" The last gate on this item said: {said}. Fix that first."
