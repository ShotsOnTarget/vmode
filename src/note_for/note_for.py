def note_for(text: str) -> str:
    """Return the role a note text's For line names.

    Inputs:
        text: the body of a note.

    Outputs:
        The role named on a well-formed For line of the
        shape "- **For**: <role>", or analyst when the
        text has no For line, or an empty or malformed one.

    Side effects:
        None. Pure.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- **For**:"):
            continue
        role = line[len("- **For**:") :].strip()
        if not role or " " in role:
            return "analyst"
        return role
    return "analyst"
