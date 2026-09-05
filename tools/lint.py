"""Shape rules ruff cannot express. Exit 1 on any violation.

Rules for code files: <= 50 lines; every function <= 50 lines; one public
function, with a docstring. Test files and conftest are exempt from length
(Board decision 2026-09-04). Every folder: exactly two files, the code file
and its test file (Board decision 2026-09-05: the note file is retired).
"""

import ast
import sys
from pathlib import Path

MAX = 50


def check_file(path: Path) -> list[str]:
    if path.name.startswith("test_") or path.name == "conftest.py":
        return []
    text = path.read_text(encoding="utf-8")
    lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    out = [f"{path}: {lines} lines"] if lines > MAX else []
    if "noqa" in text:
        out.append(f"{path}: contains noqa; suppressions are not allowed")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            span = node.end_lineno - node.lineno + 1
            if span > MAX:
                out.append(f"{path}:{node.lineno} {node.name} is {span} lines")
    public = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")
    ]
    if len(public) != 1:
        out.append(f"{path}: {len(public)} public functions")
    elif ast.get_docstring(public[0]) is None:
        out.append(f"{path}: {public[0].name} has no docstring")
    return out


def check_folder(folder: Path) -> list[str]:
    name = folder.name
    files = sorted(p.name for p in folder.iterdir() if p.name != "__pycache__")
    want = sorted([f"{name}.py", f"test_{name}.py"])
    tests_first = files == [f"test_{name}.py"]  # the code job has not landed yet
    return [] if files == want or tests_first else [f"{folder}: files {files}"]


def main() -> int:
    root = Path("src")
    problems = []
    for folder in sorted(
        p for p in root.iterdir() if p.is_dir() and p.name != "__pycache__"
    ):
        problems += check_folder(folder)
        for py in folder.glob("*.py"):
            problems += check_file(py)
    print("\n".join(problems) or "shape ok")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
