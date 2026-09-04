import json

import pytest

from wiki_read.wiki_read import wiki_read
from wiki_write.wiki_write import wiki_write


def _page(pattern="Some pattern text."):
    return {
        "id": "p1",
        "title": "Title One",
        "pattern": pattern,
        "evidence": ["ev1", "ev2"],
        "cost": 3,
        "fix": "Do the fix.",
        "created": "2024-01-01T00:00:00",
        "last_used": "2024-01-02T00:00:00",
        "times_used": 5,
    }


def _write_raw(root, page):
    keys = ("id", "title", "evidence", "cost", "created", "last_used", "times_used")
    lines = (
        ["---"]
        + [f"{k}: {json.dumps(page[k])}" for k in keys]
        + ["---", "## Pattern", "", page["pattern"], "", "## Fix", "", page["fix"], ""]
    )
    with open(f"{root}/{page['id']}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def test_roundtrip_equal(tmp_path):
    page = _page()
    _write_raw(str(tmp_path), page)
    assert wiki_read(str(tmp_path), "p1") == page


def test_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        wiki_read(str(tmp_path), "nope")


def test_malformed_raises(tmp_path):
    p = tmp_path / "bad.md"
    p.write_text(
        "---\nid bad_line\n---\n## Pattern\n\nt\n\n## Fix\n\nt\n", encoding="utf-8"
    )
    with pytest.raises(ValueError):
        wiki_read(str(tmp_path), "bad")


def test_multiline_pattern_preserved(tmp_path):
    page = _page(pattern="Paragraph one.\n\nParagraph two.")
    wiki_write(str(tmp_path), page)
    assert wiki_read(str(tmp_path), "p1") == page
