import json
import os


def wiki_write(root: str, page: dict) -> str:
    expected = {
        "id", "title", "pattern", "evidence", "cost",
        "fix", "created", "last_used", "times_used",
    }
    actual = set(page.keys())
    if actual != expected:
        raise ValueError("page has missing or extra fields")

    if not page["evidence"]:
        raise ValueError("evidence is empty")

    for item in page["evidence"]:
        if "src/" in item:
            raise ValueError("evidence must not reference code")

    os.makedirs(root, exist_ok=True)
    path = os.path.join(root, f"{page['id']}.md")

    lines = ["---"]
    for key in ("id", "title", "evidence", "cost", "created", "last_used", "times_used"):
        lines.append(f"{key}: {json.dumps(page[key])}")
    lines.append("---")
    lines.append("## Pattern")
    lines.append("")
    lines.append(page["pattern"])
    lines.append("")
    lines.append("## Fix")
    lines.append("")
    lines.append(page["fix"])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return path
