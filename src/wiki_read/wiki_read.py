import json
import os


def wiki_read(root: str, page_id: str) -> dict:
    path = os.path.join(root, f"{page_id}.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise ValueError("malformed front matter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("malformed front matter")

    page = {}
    for line in lines[1:end]:
        if ": " not in line:
            raise ValueError("malformed front matter")
        key, raw_value = line.split(": ", 1)
        try:
            page[key] = json.loads(raw_value)
        except json.JSONDecodeError:
            raise ValueError("malformed front matter")

    rest = "\n".join(lines[end + 1 :])
    pattern_marker = "## Pattern"
    fix_marker = "## Fix"
    pattern_idx = rest.find(pattern_marker)
    fix_idx = rest.find(fix_marker)
    if pattern_idx == -1 or fix_idx == -1 or fix_idx < pattern_idx:
        raise ValueError("malformed front matter")

    pattern = rest[pattern_idx + len(pattern_marker) : fix_idx].strip()
    fix = rest[fix_idx + len(fix_marker) :].strip()

    page["pattern"] = pattern
    page["fix"] = fix
    return page
