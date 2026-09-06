from builder_prompt.builder_prompt import builder_prompt


def role_prompt(item: dict, role: str, root: str) -> str:
    """Pick the prompt for one work item and role.

    Inputs: item with id and kind; role name; root working directory.
    Outputs: the builder prompt for code or test kinds, else the role text.
    Side effects: none.
    """
    if item["kind"] in ("code", "test"):
        return builder_prompt(item, role, root)
    return (
        f"You are the {role}. Working directory: {root}. "
        f"Read roles/{role}/SKILL.md and follow it exactly. "
        f"Your work item id is {item['id']}. "
        "Fetch it from the record with the work-record skill "
        "(roles/work-record/SKILL.md). Do only that item. "
        "When you are done, say what you did in one paragraph and nothing else."
    )
