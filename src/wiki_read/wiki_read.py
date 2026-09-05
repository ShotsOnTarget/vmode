import json
import os


def _parse_fields(field_lines: list[str]) -> dict:
    page = {}
    for line in field_lines:
        if ": " not in line:
            raise ValueError("malformed front matter")
        key, raw_value = line.split(": ", 1)
        try:
            page[key] = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise ValueError("malformed front matter") from exc
    return page


def _split_front_matter(lines: list[str]) -> tuple[dict, str]:
    if not lines or lines[0] != "---":
        raise ValueError("malformed front matter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("malformed front matter") from exc
    page = _parse_fields(lines[1:end])
    return page, "\n".join(lines[end + 1 :])


def _extract_sections(rest: str) -> tuple[str, str]:
    pattern_idx = rest.find("## Pattern")
    fix_idx = rest.find("## Fix")
    if pattern_idx == -1 or fix_idx == -1 or fix_idx < pattern_idx:
        raise ValueError("malformed front matter")
    pattern = rest[pattern_idx + len("## Pattern") : fix_idx].strip()
    fix = rest[fix_idx + len("## Fix") :].strip()
    return pattern, fix


def wiki_read(root: str, page_id: str) -> dict:
    """Read a wiki page written by wiki_write and return it as a dict."""
    path = os.path.join(root, f"{page_id}.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, encoding="utf-8") as f:
        text = f.read()

    page, rest = _split_front_matter(text.split("\n"))
    page["pattern"], page["fix"] = _extract_sections(rest)
    return page
