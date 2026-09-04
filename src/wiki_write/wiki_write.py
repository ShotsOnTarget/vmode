import json
import os

_REQUIRED_FIELDS = (
    "id",
    "title",
    "pattern",
    "evidence",
    "cost",
    "fix",
    "created",
    "last_used",
    "times_used",
)
_HEADER_FIELDS = tuple(f for f in _REQUIRED_FIELDS if f not in ("pattern", "fix"))


def _validate_page(page: dict) -> None:
    if set(page.keys()) != set(_REQUIRED_FIELDS):
        raise ValueError("page has missing or extra fields")
    if not page["evidence"]:
        raise ValueError("evidence is empty")
    if any("src/" in item for item in page["evidence"]):
        raise ValueError("evidence must not reference code")


def _render_lines(page: dict) -> list[str]:
    lines = ["---"]
    lines += [f"{k}: {json.dumps(page[k])}" for k in _HEADER_FIELDS]
    lines += ["---", "## Pattern", "", page["pattern"], "", "## Fix", "", page["fix"]]
    return lines


def wiki_write(root: str, page: dict) -> str:
    _validate_page(page)
    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, f"{page['id']}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(_render_lines(page)) + "\n")
    return path
