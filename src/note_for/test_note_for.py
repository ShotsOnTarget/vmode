from note_for.note_for import note_for


def test_for_line_returns_role():
    text = (
        "- **Work item id**: vm-1\n"
        "- **From**: Supervisor\n"
        "- **For**: architect\n"
        "- **What failed**: gate checks did not pass.\n"
    )
    assert note_for(text) == "architect"


def test_for_line_returns_engineer():
    text = (
        "- **Work item id**: vm-1\n"
        "- **From**: Supervisor\n"
        "- **For**: engineer\n"
        "- **What failed**: gate checks did not pass.\n"
    )
    assert note_for(text) == "engineer"


def test_no_for_line_returns_analyst():
    text = (
        "- **Work item id**: vm-1\n"
        "- **From**: Supervisor\n"
        "- **What failed**: gate checks did not pass.\n"
    )
    assert note_for(text) == "analyst"


def test_empty_for_line_returns_analyst():
    text = "- **For**:\n"
    assert note_for(text) == "analyst"


def test_malformed_for_line_returns_analyst():
    text = "- **For**: whoever is on call\n"
    assert note_for(text) == "analyst"
