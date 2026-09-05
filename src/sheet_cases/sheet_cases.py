import re

_CASE = re.compile(r"^\s*-\s*`test_(\w+)`\s*:?\s*(.*)$")


def sheet_cases(sheet: str) -> list[str]:
    """Test case names a sheet requires, in sheet order, without test_.

    A case line is `- \\`test_name\\`: description`. A line whose description
    starts with the word removed (any case) names a case the sheet retires:
    it is excluded, and the gate then treats its absence as correct rather
    than as case_missing.
    """
    names = []
    for line in sheet.splitlines():
        match = _CASE.match(line)
        if not match:
            continue
        name, text = match.group(1), match.group(2).strip().lower()
        if text.startswith("removed") or text.startswith("remove "):
            continue
        if name not in names:
            names.append(name)
    return names
