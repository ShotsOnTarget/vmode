import json
import os
from datetime import datetime, timedelta

from wiki_stale.wiki_stale import wiki_stale

NOW = "2026-01-30T00:00:00"


def _write_page(root, page_id, last_used):
    os.makedirs(root, exist_ok=True)
    lines = ["---"]
    for key, val in (
        ("id", page_id), ("title", "t"), ("evidence", ["e"]),
        ("cost", "c"), ("created", last_used), ("last_used", last_used),
        ("times_used", 1),
    ):
        lines.append(f"{key}: {json.dumps(val)}")
    lines.append("---")
    lines.append("## Pattern")
    lines.append("")
    lines.append("p")
    lines.append("")
    lines.append("## Fix")
    lines.append("")
    lines.append("f")
    with open(os.path.join(root, f"{page_id}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def test_old_page_listed(tmp_path):
    last_used = (datetime.fromisoformat(NOW) - timedelta(days=40)).isoformat()
    _write_page(tmp_path, "old", last_used)
    assert wiki_stale(str(tmp_path), 30, NOW) == ["old"]


def test_fresh_page_not_listed(tmp_path):
    last_used = (datetime.fromisoformat(NOW) - timedelta(days=5)).isoformat()
    _write_page(tmp_path, "fresh", last_used)
    assert wiki_stale(str(tmp_path), 30, NOW) == []


def test_readme_skipped(tmp_path):
    with open(os.path.join(tmp_path, "README.md"), "w", encoding="utf-8") as f:
        f.write("not a page")
    assert wiki_stale(str(tmp_path), 30, NOW) == []


def test_missing_root_empty():
    assert wiki_stale("/no/such/dir", 30, NOW) == []
