def _normalize(name: str) -> str:
    """Key for a raw field name."""
    return name.split("(", 1)[0].strip().lower().replace(" ", "_")


def _field(stripped: str) -> tuple[str, str] | None:
    """Split a field line into key and value, else None."""
    if not stripped.startswith("- **"):
        return None
    end = stripped.find("**:", 4)
    if end == -1:
        return None
    return (_normalize(stripped[4:end]), stripped[end + 3 :].strip())


def _case_name(raw: str) -> str | None:
    """Backtick name on a case continuation line, else None."""
    if not raw.lstrip().startswith("- `"):
        return None
    first = raw.find("`")
    second = raw.find("`", first + 1)
    if first == -1 or second == -1:
        return None
    return raw[first + 1 : second]


def _case_list(lines: list) -> list:
    """Case names from a cases field's continuation lines."""
    names = []
    for raw in lines:
        name = _case_name(raw)
        if name is not None:
            names.append(name)
    return names


def sheet_fields(text: str) -> dict:
    """Parse an instruction sheet into a field dict.

    Inputs:
        text: an instruction sheet in the shape of
            roles/shared/instruction-sheet.md, any length, may be empty.

    Outputs:
        A dict of normalized field names to values with continuation
        lines appended, plus a `cases` list when any field exists.

    Side effects:
        None.
    """
    fields = {}
    conts = {}
    current = None
    for line in text.splitlines():
        found = _field(line.lstrip())
        if found is not None:
            key, value = found
            fields[key] = value
            conts[key] = []
            current = key
            continue
        if current is None:
            continue
        fields[current] = fields[current] + "\n" + line.strip()
        conts[current].append(line)
    if not fields:
        return {}
    fields["cases"] = _case_list(conts.get("cases", []))
    return fields
