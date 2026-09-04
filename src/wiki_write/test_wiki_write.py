import pytest

from wiki_write.wiki_write import wiki_write


def make_page(title="A title", fix="Do the fix"):
    return {
        "id": "p1",
        "title": title,
        "pattern": "Some pattern",
        "evidence": ["it broke once"],
        "cost": 3,
        "fix": fix,
        "created": "2026-01-01T00:00:00",
        "last_used": "2026-01-01T00:00:00",
        "times_used": 1,
    }


def test_write_creates_file(tmp_path):
    path = wiki_write(str(tmp_path), make_page())
    with open(path) as f:
        content = f.read()
    assert content.startswith("---")
    import os

    assert os.path.exists(path)


def test_missing_field_rejected(tmp_path):
    page = make_page()
    del page["fix"]
    with pytest.raises(ValueError):
        wiki_write(str(tmp_path), page)
    import os

    assert os.listdir(str(tmp_path)) == []


def test_code_reference_rejected(tmp_path):
    page = make_page()
    page["evidence"] = ["src/x/x.py"]
    with pytest.raises(ValueError):
        wiki_write(str(tmp_path), page)


def test_overwrite_replaces(tmp_path):
    wiki_write(str(tmp_path), make_page(title="First"))
    path = wiki_write(str(tmp_path), make_page(title="Second"))
    with open(path) as f:
        content = f.read()
    assert "Second" in content
    assert "First" not in content
