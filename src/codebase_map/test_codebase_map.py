from pathlib import Path

from codebase_map.codebase_map import codebase_map


def _write(root: Path, name: str, text: str | None = None) -> None:
    folder = root / "src" / name
    folder.mkdir(parents=True, exist_ok=True)
    if text is not None:
        (folder / f"{name}.py").write_text(text)


def test_one_line_per_folder_sorted(tmp_path):
    for name in ["a", "c", "b"]:
        _write(tmp_path, name, f"def {name}(): pass\n")
    assert codebase_map(str(tmp_path)) == ["a(): ", "b(): ", "c(): "]


def test_signature_and_docstring(tmp_path):
    _write(tmp_path, "f", 'def f(x: int, y=2) -> str:\n    """Add."""\n')
    assert codebase_map(str(tmp_path)) == ["f(x: int, y) -> str: Add."]


def test_no_annotations_and_no_docstring(tmp_path):
    _write(tmp_path, "f", "def f(a, b):\n    pass\n")
    assert codebase_map(str(tmp_path)) == ["f(a, b): "]


def test_missing_file_marked(tmp_path):
    _write(tmp_path, "mymod")
    assert codebase_map(str(tmp_path)) == ["mymod: missing"]


def test_unparsable_marked(tmp_path):
    _write(tmp_path, "bad", "def (:\n")
    assert codebase_map(str(tmp_path)) == ["bad: unparsable"]


def test_no_matching_function_marked(tmp_path):
    _write(tmp_path, "mymod", "def other(): pass\n")
    assert codebase_map(str(tmp_path)) == ["mymod: no public function"]


def test_underscore_folders_skipped(tmp_path):
    _write(tmp_path, "ok", "def ok(): pass\n")
    (tmp_path / "src" / "__pycache__").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / ".hidden").mkdir(parents=True, exist_ok=True)
    assert codebase_map(str(tmp_path)) == ["ok(): "]


def test_no_src_raises(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    try:
        codebase_map(str(root))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
