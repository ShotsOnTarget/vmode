from existing_tests.existing_tests import existing_tests

TEST = (
    "def test_zero():\n"
    "    pass\n\n\n"
    "def test_alpha():\n"
    "    pass\n\n\n"
    "def helper():\n"
    "    pass\n\n\n"
    "def test_mid():\n"
    "    pass\n"
)


def _write(repo, folder, text):
    d = repo / "src" / folder
    d.mkdir(parents=True)
    (d / f"test_{folder}.py").write_text(text)


def test_lists_test_functions_in_file_order(tmp_path):
    _write(tmp_path, "widget", TEST)
    assert existing_tests("widget", str(tmp_path)) == [
        "test_zero",
        "test_alpha",
        "test_mid",
    ]


def test_missing_test_file_returns_empty(tmp_path):
    d = tmp_path / "src" / "widget"
    d.mkdir(parents=True)
    (d / "widget.py").write_text("def widget():\n    pass\n")
    assert existing_tests("widget", str(tmp_path)) == []
